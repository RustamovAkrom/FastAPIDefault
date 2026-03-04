from fastapi import Request

from db.models.user import UserRole


def get_current_role(request: Request) -> UserRole | None:
    role_raw = request.session.get("role")
    if isinstance(role_raw, str):
        try:
            return UserRole(role_raw)
        except ValueError:
            return None
    return None


def can_edit_role(request: Request) -> bool:
    role = get_current_role(request)
    return role == UserRole.SUPERADMIN


def can_delete_user(request: Request, target_role: UserRole, actor_id: int | None, target_id: int) -> bool:
    role = get_current_role(request)

    if target_role == UserRole.SUPERADMIN:
        return False

    if actor_id == target_id:
        return False

    if role == UserRole.ADMIN and target_role == UserRole.ADMIN:
        return False

    return True
