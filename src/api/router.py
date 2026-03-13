import importlib
import pkgutil
from types import ModuleType

from fastapi.routing import APIRouter


def _iter_v1_modules() -> list[ModuleType]:
    modules: list[ModuleType] = []
    package = importlib.import_module("api.api_v1")

    for module_info in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):
        modules.append(importlib.import_module(module_info.name))

    return modules


api_router = APIRouter()

for module in _iter_v1_modules():
    router = getattr(module, "router", None)
    if isinstance(router, APIRouter):
        api_router.include_router(router)
