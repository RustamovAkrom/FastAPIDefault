from typing import ClassVar

from infrastructure.admin.base import BaseAdmin
from infrastructure.admin.registry import register_admin
from modules.dummy.models import Dummy


@register_admin
class DummyAdmin(BaseAdmin, model=Dummy):  # type: ignore[call-arg, misc]
    name: ClassVar[str] = "Dummy"
    name_plural: ClassVar[str] = "Dummy"

    icon: ClassVar[str] = "fa-solid fa-database"
    column_list: ClassVar = (
        Dummy.id,
        Dummy.name,
    )
