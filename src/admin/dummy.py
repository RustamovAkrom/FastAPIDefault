from core.admin.base import BaseAdmin
from core.admin.registry import register_admin
from db.models.dummy import Dummy


@register_admin
class DummyAdmin(BaseAdmin, model=Dummy):  # type: ignore[misc]
    column_list = (
        Dummy.id,
        Dummy.name,
    )
