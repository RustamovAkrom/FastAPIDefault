import importlib
import pkgutil
from collections.abc import Iterator
from pathlib import Path

from fastapi import APIRouter

from core.logger import configure_logger
from infrastructure.admin.registry import register_admin
from modules.base import BaseModule

logger = configure_logger()

MODULES_PATH = Path(__file__).parent
MODULES_PACKAGE = __name__

# Safe loaded modules
loaded_modules: list[BaseModule] = []


def iter_modules() -> Iterator[str]:
    for module in pkgutil.iter_modules([str(MODULES_PATH)]):
        if module.ispkg:
            yield module.name


def sort_modules(modules: list[BaseModule]) -> list[BaseModule]:
    """
    Sort modules based on dependencies.
    """

    result = []
    visited = set()

    def visit(module: BaseModule) -> None:
        if module.name in visited:
            return

        for dep in module.dependencies:
            dep_module = next((m for m in modules if m.name == dep), None)

            if dep_module:
                visit(dep_module)

        visited.add(module.name)
        result.append(module)

    for module in modules:
        visit(module)

    return result


def load_modules() -> APIRouter:
    """
    Discover modules and register components.
    """

    api_router = APIRouter()

    logger.info("Loading modules")

    modules: list[BaseModule] = []

    # 1️⃣ discover modules
    for module_name in iter_modules():
        module_path = f"{MODULES_PACKAGE}.{module_name}.module"

        try:
            mod = importlib.import_module(module_path)
        except Exception:
            logger.exception("Module import failed", module=module_name)
            continue

        module_class = getattr(mod, "Module", None)

        if module_class is None or not issubclass(module_class, BaseModule):
            logger.warning("Invalid module", module=module_name)
            continue

        module = module_class()
        modules.append(module)

    # 2️⃣ sort by dependencies
    modules = sort_modules(modules)

    # 3️⃣ register modules
    for module in modules:
        loaded_modules.append(module)

        logger.info("Registering module", module=module.name)

        if module.router:
            api_router.include_router(module.router)

        for view in module.admin_views:
            register_admin(view)

        module.startup()

    logger.info("Modules loaded")

    return api_router
