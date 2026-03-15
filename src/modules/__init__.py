import importlib
import pkgutil
from pathlib import Path

from fastapi import APIRouter

MODULES_PACKAGE = "modules"
MODULES_PATH = Path(__file__).parent


def load_models() -> None:
    """
    Import all models from modules/*/models.py
    so SQLAlchemy can register them.
    """

    for module in pkgutil.iter_modules([str(MODULES_PATH)]):
        module_name = module.name
        models_file = MODULES_PATH / module_name / "models.py"

        if models_file.exists():
            importlib.import_module(f"{MODULES_PACKAGE}.{module_name}.models")


def load_routers() -> APIRouter:
    """
    Automatically discover routers from modules
    and return combined APIRouter
    """

    router = APIRouter()

    for module in pkgutil.iter_modules([str(MODULES_PATH)]):
        module_name = module.name
        router_file = MODULES_PATH / module_name / "router.py"

        if not router_file.exists():
            continue

        mod = importlib.import_module(f"{MODULES_PACKAGE}.{module_name}.router")

        module_router = getattr(mod, "router", None)

        if module_router:
            router.include_router(module_router)

    return router


def load_admin() -> None:
    """
    Auto-discover admin.py inside modules
    """

    for module in pkgutil.iter_modules([str(MODULES_PATH)]):
        module_name = module.name
        admin_file = MODULES_PATH / module_name / "admin.py"

        if not admin_file.exists():
            continue

        importlib.import_module(f"{MODULES_PACKAGE}.{module_name}.admin")
