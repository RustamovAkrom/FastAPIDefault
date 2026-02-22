from sqladmin.filters import BooleanFilter, AllUniqueStringValuesFilter
from sqladmin import action
from sqladmin.exceptions import SQLAdminException

from admin.registry import register_admin
from db.models.user import User, UserRole
from .base import BaseAdmin
from core.database import async_session
from core.security import hash_password


@register_admin
class UserAdmin(BaseAdmin, model=User):

    # =======================
    # Columns configuration
    # =======================

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
    # UI formatting
    # =======================

    column_formatters = {
        User.is_active: lambda m, a: "🟢 Active" if m.is_active else "🔴 Disabled",
        User.role: lambda m, a: f"👑 {m.role.value}",
    }

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

    async def on_model_change(self, data, model, is_created, request):

        current_role = request.session.get("role")
        current_user_id = request.session.get("admin_user_id")

        # Normalize role value from form
        new_role = data.get("role")

        if isinstance(new_role, str):
            try:
                new_role = UserRole(new_role.lower())
            except ValueError:
                new_role = UserRole[new_role]

        # ===== RBAC RULES =====

        # Admin cannot assign SUPERADMIN role
        if current_role == UserRole.ADMIN and new_role == UserRole.SUPERADMIN:
            raise SQLAdminException("Admin cannot assign SUPERADMIN role.")

        # Nobody can edit SUPERADMIN
        if not is_created and model.role == UserRole.SUPERADMIN:
            raise SQLAdminException("SUPERADMIN cannot be modified.")

        # Prevent changing own role
        if not is_created and model.id == current_user_id:
            if new_role != model.role:
                raise SQLAdminException("You cannot change your own role.")

        # ===== PASSWORD HANDLING =====

        raw_password = data.get("password")

        if is_created:
            if not raw_password:
                raise SQLAdminException("Password is required when creating a user.")

            data["password"] = hash_password(raw_password)

        else:
            # update password only if provided
            if raw_password:
                data["password"] = hash_password(raw_password)
            else:
                data.pop("password", None)

    async def on_model_delete(self, model, request):

        current_user_id = request.session.get("admin_user_id")
        current_role = request.session.get("role")

        # Cannot delete SUPERADMIN
        if model.role == UserRole.SUPERADMIN:
            raise SQLAdminException("SUPERADMIN cannot be deleted.")

        # Cannot delete yourself
        if model.id == current_user_id:
            raise SQLAdminException("You cannot delete your own account.")

        # Admin cannot delete another admin
        if current_role == UserRole.ADMIN and model.role == UserRole.ADMIN:
            raise SQLAdminException("Admin cannot delete another admin.")

    # =========================================================
    # ADMIN ACTIONS
    # =========================================================

    @action(
        name="deactivate_users",
        label="Deactivate selected users",
        confirmation_message="Are you sure you want to deactivate selected users?"
    )
    async def deactivate_users(self, request, ids):

        async with async_session() as session:
            for user_id in ids:
                user = await session.get(User, user_id)

                if user.role == UserRole.SUPERADMIN:
                    continue  # skip superadmin

                user.is_active = False

            await session.commit()