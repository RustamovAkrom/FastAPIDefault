from collections.abc import Iterable
from typing import Any

from fastapi import APIRouter


class BaseModule:
    """
    Base contract for application modules.
    """

    name: str

    router: APIRouter | None = None

    models: Iterable[type[Any]] = ()

    admin_views: Iterable[type[Any]] = ()

    tasks: Iterable[Any] = ()

    # зависимости от других модулей
    dependencies: tuple[str, ...] = ()

    def startup(self) -> None:
        """Optional startup hook."""
        pass

    def shutdown(self) -> None:
        """Optional shutdown hook."""
        pass
