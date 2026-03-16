from collections.abc import Sequence
from typing import Any, ClassVar

from fastapi import Request
from sqladmin import ModelView
from sqlalchemy.orm import InstrumentedAttribute

from infrastructure.admin.permissions import get_role
from modules.users.models import UserRole


class BaseAdmin(ModelView):
    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True
    can_view_details: ClassVar[bool] = True

    page_size: ClassVar[int] = 50

    column_searchable_list: ClassVar[Sequence[str | InstrumentedAttribute[Any]]] = ()
    column_sortable_list: ClassVar[Sequence[str | InstrumentedAttribute[Any]]] = ()

    column_default_sort: ClassVar[tuple[str | InstrumentedAttribute[Any], bool]] = ("id", True)

    def is_accessible(self, request: Request) -> bool:
        role = get_role(request)
        return role in {UserRole.ADMIN, UserRole.SUPERADMIN}
