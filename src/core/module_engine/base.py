from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field


class ModuleSpec(BaseModel):
    """Validated metadata for module discovery and dependency ordering."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1)
    dependencies: tuple[str, ...] = ()


class BaseModule:
    """
    Contract for all business modules.

    Modules are discovered from `src/modules/*/module.py` and should expose
    a `Module` class inheriting from this base.
    """

    name: str = ""
    router: APIRouter | None = None
    models: tuple[type[Any], ...] = ()
    admin_views: tuple[type[Any], ...] = ()
    tasks: tuple[Any, ...] = ()
    middlewares: tuple[tuple[type, dict[str, Any]], ...] = ()
    dependencies: tuple[str, ...] = ()

    @property
    def spec(self) -> ModuleSpec:
        return ModuleSpec(name=self.name, dependencies=self.dependencies)

    def startup(self) -> None:
        """Optional startup hook."""

    def shutdown(self) -> None:
        """Optional shutdown hook."""
