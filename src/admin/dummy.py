from core.admin import BaseAdmin, register_admin
from db.models.dummy import Dummy


@register_admin
class DummyAdmin(BaseAdmin, model=Dummy):  # type: ignore[call-arg, misc]
    column_list = [Dummy.id, Dummy.name]
