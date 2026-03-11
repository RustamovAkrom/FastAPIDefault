from collections.abc import Sequence
from typing import ClassVar

from fastapi import Request
from sqladmin import ModelView

from core.admin.permissions import get_role
from db.models.user import UserRole


class BaseAdmin(ModelView):
    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True
    can_view_details: ClassVar[bool] = True

    page_size: ClassVar[int] = 50

    column_searchable_list: ClassVar[Sequence[str]] = ()
    column_sortable_list: ClassVar[Sequence[str]] = ()

    column_default_sort: ClassVar[tuple[str, bool]] = ("id", True)

    def is_accessible(self, request: Request) -> bool:
        role = get_role(request)
        return role in {UserRole.ADMIN, UserRole.SUPERADMIN}
