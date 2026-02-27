from core.admin import BaseAdmin, register_admin
from db.models.dummy import Dummy


@register_admin
class DummyAdmin(BaseAdmin, model=Dummy):
    column_list = [Dummy.id, Dummy.name]
