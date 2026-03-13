import importlib
import pkgutil
from pathlib import Path


def load_all_models() -> None:
    """
    Automatically import all admin modules.

    This allows adding new admin views simply by
    creating a file inside the admin package.
    """

    package_dir = Path(__file__).resolve().parent
    package_name = "admin"

    for module in pkgutil.walk_packages(
        [str(package_dir)],
        prefix=f"{package_name}.",
    ):
        importlib.import_module(module.name)
