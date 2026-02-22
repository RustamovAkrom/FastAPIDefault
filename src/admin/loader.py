import importlib
import pkgutil


def load_admin_modules() -> None:
    """
    Avtomaticaly importing all files from src/admin
    """
    package = "src.admin"

    for _, module_name, _ in pkgutil.iter_modules(["src/admin"]):
        if module_name.startswith("_"):
            continue
        importlib.import_module(f"{package}.{module_name}")
