from collections.abc import Callable, Iterable
from typing import Any, ClassVar

from fastapi import Request
from sqladmin import action
from sqladmin.exceptions import SQLAdminException
from sqladmin.filters import AllUniqueStringValuesFilter, BooleanFilter

from core.admin.base import BaseAdmin
from core.admin.permissions import get_role, get_user_id
from core.admin.registry import register_admin
from core.database import async_session
from core.logger import configure_logger
from core.security import hash_password
from db.models.user import User, UserRole


@register_admin
class UserAdmin(BaseAdmin, model=User):  # type: ignore[call-arg]
    logger = configure_logger()

    # =====================
    # PERMISSIONS
    # =====================

    can_delete: ClassVar[bool] = True
    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_view_details: ClassVar[bool] = True

    # =====================
    # LIST VIEW
    # =====================

    column_list: ClassVar = (
        User.id,
        User.username,
        User.email,
        User.role,
        User.is_active,
    )

    column_searchable_list: ClassVar = (
        User.username,
        User.email,
    )

    column_sortable_list: ClassVar = (
        User.id,
        User.username,
        User.role,
    )

    column_filters: ClassVar = (
        BooleanFilter(User.is_active),
        AllUniqueStringValuesFilter(User.role),
    )

    column_details_exclude_list: ClassVar = (User.password,)

    # =====================
    # UI FORMATTERS
    # =====================

    @staticmethod
    def format_is_active(model: User, _: Any) -> str:
        return "🟢 Active" if model.is_active else "🔴 Disabled"

    @staticmethod
    def format_role(model: User, _: Any) -> str:
        return f"👑 {model.role.value}"

    column_formatters: ClassVar[dict[Any, Callable[..., Any]]] = {
        User.is_active: format_is_active,
        User.role: format_role,
    }

    # =====================
    # FORM OPTIONS
    # =====================

    form_choices: ClassVar = {"role": [(role.value, role.name.title()) for role in UserRole]}

    # =====================
    # META
    # =====================

    name: ClassVar[str] = "User"
    name_plural: ClassVar[str] = "Users"

    icon: ClassVar[str] = "fa-solid fa-user"
    identity: ClassVar[str] = "user"

    category: ClassVar[str] = "Accounts"
    category_icon: ClassVar[str] = "fa-solid fa-user"

    # =====================================================
    # ACCESS CONTROL
    # =====================================================

    def is_accessible(self, request: Request) -> bool:
        role = get_role(request)
        return role in {UserRole.ADMIN, UserRole.SUPERADMIN}

    # =====================================================
    # MODEL VALIDATION
    # =====================================================

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: User,
        is_created: bool,
        request: Request,
    ) -> None:
        actor_role = get_role(request)
        actor_id = get_user_id(request)

        # normalize email
        email_raw = data.get("email")
        if isinstance(email_raw, str):
            data["email"] = email_raw.strip().lower()

        # normalize role
        new_role: UserRole | None = None
        role_raw = data.get("role")

        if isinstance(role_raw, str):
            try:
                new_role = UserRole(role_raw)
            except ValueError:
                pass

        # ===== RBAC =====

        if actor_role == UserRole.ADMIN and new_role == UserRole.SUPERADMIN:
            raise SQLAdminException("🚫 Admin cannot assign SUPERADMIN role.")

        if not is_created and model.role == UserRole.SUPERADMIN:
            raise SQLAdminException("🚫 SUPERADMIN cannot be modified.")

        if not is_created and actor_id == model.id and new_role and new_role != model.role:
            raise SQLAdminException("⚠ You cannot change your own role.")

        # ===== PASSWORD =====

        raw_password = data.get("password")

        if is_created:
            if not isinstance(raw_password, str) or not raw_password:
                raise SQLAdminException("Password is required when creating a user.")

            data["password"] = hash_password(raw_password)

        else:
            if isinstance(raw_password, str) and raw_password:
                data["password"] = hash_password(raw_password)
            else:
                data.pop("password", None)

    # =====================================================
    # DELETE VALIDATION
    # =====================================================

    async def on_model_delete(self, model: User, request: Request) -> None:
        actor_id = get_user_id(request)
        actor_role = get_role(request)

        if model.role == UserRole.SUPERADMIN:
            raise SQLAdminException("🚫 SUPERADMIN cannot be deleted.")

        if actor_id == model.id:
            raise SQLAdminException("⚠ You cannot delete your own account.")

        if actor_role == UserRole.ADMIN and model.role == UserRole.ADMIN:
            raise SQLAdminException("🚫 Admin cannot delete another admin.")

    # =====================================================
    # ADMIN ACTIONS
    # =====================================================

    @action(
        name="deactivate_users",
        label="Deactivate selected users",
        confirmation_message="Are you sure you want to deactivate selected users?",
    )
    async def deactivate_users(
        self,
        request: Request,
        ids: Iterable[int],
    ) -> None:
        async with async_session() as session:
            for user_id in ids:
                user: User | None = await session.get(User, user_id)

                if user is None:
                    continue

                if user.role == UserRole.SUPERADMIN:
                    continue

                user.is_active = False

            await session.commit()
