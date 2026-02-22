from sqladmin import ModelView

from admin.registry import register_admin
from db.models.dummy import Dummy
from .base import BaseAdmin

@register_admin
class DummyAdmin(BaseAdmin, model=Dummy):
    column_list = [Dummy.id, Dummy.name]
