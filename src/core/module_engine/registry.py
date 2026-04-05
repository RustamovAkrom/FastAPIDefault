import importlib
import pkgutil
from collections.abc import Iterator
from pathlib import Path

from fastapi import APIRouter
from pydantic import ValidationError

from core.logger import configure_logger
from core.module_engine.base import BaseModule, ModuleSpec
from modules.platform_admin.registry import register_admin

logger = configure_logger()

MODULES_PATH = Path(__file__).resolve().parent.parents[1] / "modules"  # src/modules
MODULES_PACKAGE = "modules"

loaded_modules: list[BaseModule] = []


class ModuleRegistryError(RuntimeError):
    """Base error for module engine failures."""


class ModuleDependencyError(ModuleRegistryError):
    """Raised when dependency graph is invalid."""


def iter_modules() -> Iterator[str]:
    for module in pkgutil.iter_modules([str(MODULES_PATH)]):
        if module.ispkg:
            yield module.name


def sort_modules(modules: list[BaseModule]) -> list[BaseModule]:
    """Topological sort with cycle and unknown-dependency checks."""
    ordered: list[BaseModule] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    by_name = {module.spec.name: module for module in modules}

    def visit(module: BaseModule) -> None:
        spec = module.spec
        if spec.name in visited:
            return
        if spec.name in visiting:
            raise ModuleDependencyError(f"Cyclic dependency detected around '{spec.name}'")

        visiting.add(spec.name)
        for dep in spec.dependencies:
            dep_module = by_name.get(dep)
            if dep_module is None:
                raise ModuleDependencyError(f"Module '{spec.name}' depends on unknown module '{dep}'")
            visit(dep_module)
        visiting.remove(spec.name)

        visited.add(spec.name)
        ordered.append(module)

    for module in modules:
        visit(module)

    return ordered


def get_loaded_modules() -> tuple[BaseModule, ...]:
    return tuple(loaded_modules)


def load_modules() -> APIRouter:
    """Discover and register business modules from `src/modules`."""
    loaded_modules.clear()
    api_router = APIRouter()

    logger.info("Loading modules", path=str(MODULES_PATH))

    modules: list[BaseModule] = []
    seen_names: set[str] = set()

    for module_name in iter_modules():
        module_path = f"{MODULES_PACKAGE}.{module_name}.module"

        try:
            mod = importlib.import_module(module_path)
        except Exception:
            logger.exception("Module import failed", module=module_name)
            continue

        module_class = getattr(mod, "Module", None)
        if module_class is None or not issubclass(module_class, BaseModule):
            logger.warning("Invalid module class", module=module_name, expected="Module(BaseModule)")
            continue

        try:
            module = module_class()
        except Exception:
            logger.exception("Module initialization failed", module=module_name)
            continue

        try:
            spec: ModuleSpec = module.spec
        except ValidationError as ex:
            logger.error("Module spec validation failed", module=module_name, error=str(ex))
            continue

        if spec.name in seen_names:
            logger.error("Duplicate module name", module=spec.name)
            continue

        seen_names.add(spec.name)
        modules.append(module)

    try:
        modules = sort_modules(modules)
    except ModuleDependencyError:
        logger.exception("Module dependency resolution failed")
        raise

    for module in modules:
        loaded_modules.append(module)

        logger.info("Registering module", module=module.spec.name)

        if module.router:
            api_router.include_router(module.router)

        for view in module.admin_views:
            register_admin(view)

        try:
            module.startup()
        except Exception:
            logger.exception("Module startup failed", module=module.spec.name)
            raise ModuleRegistryError(f"Startup failed for module '{module.spec.name}'") from None

    logger.info("Modules loaded", count=len(loaded_modules))

    return api_router
