from typing import ClassVar

from modules.dummy.models import Dummy
from modules.platform_admin.base import BaseAdmin
from modules.platform_admin.registry import register_admin


@register_admin
class DummyAdmin(BaseAdmin, model=Dummy):  # type: ignore[call-arg, misc]
    name: ClassVar[str] = "Dummy"
    name_plural: ClassVar[str] = "Dummy"

    icon: ClassVar[str] = "fa-solid fa-database"
    column_list: ClassVar = (
        Dummy.id,
        Dummy.name,
    )
