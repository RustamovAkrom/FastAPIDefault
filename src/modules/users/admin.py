from collections.abc import Callable, Iterable
from typing import Any, cast

from fastapi import Request
from sqladmin import action
from sqladmin.exceptions import SQLAdminException
from sqladmin.filters import AllUniqueStringValuesFilter, BooleanFilter

from infrastructure.admin.base import BaseAdmin
from infrastructure.admin.registry import register_admin
from core.database import async_session
from core.logger import configure_logger
from core.security import hash_password
from modules.users.models import User, UserRole

Formatter = Callable[[Any, Any], Any]


@register_admin
class UserAdmin(BaseAdmin, model=User):  # type: ignore[call-arg, misc]
    logger = configure_logger()

    column_list = [
        User.id,
        User.username,
        User.email,
        User.role,
        User.is_active,
    ]

    column_searchable_list = [
        User.username,
        User.email,
    ]

    column_sortable_list = [
        User.id,
        User.username,
        User.role,
    ]

    column_filters = [
        BooleanFilter(User.is_active),
        AllUniqueStringValuesFilter(User.role),
    ]

    column_details_exclude_list = [
        User.password,
    ]

    # =======================
    # UI formatting (MYPY SAFE)
    # =======================

    @staticmethod
    def format_is_active(model: User, _: Any) -> str:
        return "🟢 Active" if model.is_active else "🔴 Disabled"

    @staticmethod
    def format_role(model: User, _: Any) -> str:
        return f"👑 {model.role}"

    column_formatters = cast(
        dict[Any, Formatter],
        {
            User.is_active: format_is_active,
            User.role: format_role,
        },
    )

    form_choices = {
        "role": [
            ("superadmin", "Super Admin"),
            ("admin", "Admin"),
            ("moderator", "Moderator"),
            ("user", "User"),
        ]
    }

    # =======================
    # Meta info
    # =======================

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    identity = "user"
    category = "Accounts"
    category_icon = "fa-solid fa-user"

    # =========================================================
    # RBAC + VALIDATION LOGIC
    # =========================================================

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: User,
        is_created: bool,
        request: Request,
    ) -> None:
        current_role: UserRole | None = request.session.get("role")
        current_user_id: int | None = request.session.get("admin_user_id")

        # Normalize role
        new_role_raw = data.get("role")
        new_role: UserRole | None = None

        if isinstance(new_role_raw, str):
            try:
                new_role = UserRole(new_role_raw.lower())
            except ValueError:
                try:
                    new_role = UserRole[new_role_raw]
                except Exception:
                    new_role = None

        # ===== RBAC RULES =====

        if current_role == UserRole.ADMIN and new_role == UserRole.SUPERADMIN:
            self.logger.warning(
                "Admin cannot assign superadmin role", extra={"actor_id": current_user_id, "target_id": model.id}
            )
            raise SQLAdminException("Admin cannot assign SUPERADMIN role.")

        if not is_created and model.role == UserRole.SUPERADMIN:
            self.logger.warning(
                "SUPERADMIN cannot be modified.",
                extra={
                    "actor_id": current_user_id,
                    "target_id": model.id,
                },
            )
            raise SQLAdminException("SUPERADMIN cannot be modified.")

        if not is_created and model.id == current_user_id:
            if new_role and new_role != model.role:
                self.logger.warning(
                    "You cannot change your own role.",
                    extra={
                        "actor_id": current_user_id,
                        "target_id": model.id,
                    },
                )
                raise SQLAdminException("You cannot change your own role.")

        # ===== PASSWORD HANDLING =====

        raw_password = data.get("password")

        if is_created:
            if not raw_password:
                self.logger.warning(
                    "Password is required when creating a user.",
                    extra={
                        "actor_id": current_user_id,
                        "target_id": model.id,
                    },
                )
                raise SQLAdminException("Password is required when creating a user.")

            data["password"] = hash_password(raw_password)

        else:
            if raw_password:
                data["password"] = hash_password(raw_password)
            else:
                data.pop("password", None)

    async def on_model_delete(self, model: User, request: Request) -> None:
        current_user_id: int | None = request.session.get("admin_user_id")
        current_role: UserRole | None = request.session.get("role")

        if model.role == UserRole.SUPERADMIN:
            self.logger.warning(
                "SUPERADMIN cannot be deleted.",
                extra={
                    "actor_id": current_user_id,
                    "target_id": model.id,
                },
            )
            raise SQLAdminException("SUPERADMIN cannot be deleted.")

        if model.id == current_user_id:
            self.logger.warning(
                "You cannot delete your own account.",
                extra={
                    "actor_id": current_user_id,
                    "target_id": model.id,
                },
            )
            raise SQLAdminException("You cannot delete your own account.")

        if current_role == UserRole.ADMIN and model.role == UserRole.ADMIN:
            self.logger.warning(
                "Admin cannot delete another admin.",
                extra={
                    "actor_id": current_user_id,
                    "target_id": model.id,
                },
            )
            raise SQLAdminException("Admin cannot delete another admin.")

    # =========================================================
    # ADMIN ACTIONS
    # =========================================================

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

                if not user:
                    continue

                if user.role == UserRole.SUPERADMIN:
                    continue

                user.is_active = False

            await session.commit()
