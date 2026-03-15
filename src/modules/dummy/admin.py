from infrastructure.admin.base import BaseAdmin
from infrastructure.admin.registry import register_admin
from modules.dummy.models import Dummy


@register_admin
class DummyAdmin(BaseAdmin, model=Dummy):  # type: ignore[call-arg, misc]
    column_list = [Dummy.id, Dummy.name]
