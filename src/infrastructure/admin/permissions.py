from fastapi import Request

from modules.users.models import UserRole


def get_role(request: Request) -> UserRole | None:
    role_raw: object | None = request.session.get("role")

    if not isinstance(role_raw, str):
        return None

    try:
        return UserRole(role_raw)
    except Exception:
        return None


def get_user_id(request: Request) -> int | None:
    user_id: object | None = request.session.get("admin_user_id")

    if isinstance(user_id, int):
        return user_id

    return None


def is_superadmin(request: Request) -> bool:
    role: UserRole | None = get_role(request)
    return role == UserRole.SUPERADMIN


def is_admin(request: Request) -> bool:
    role: UserRole | None = get_role(request)
    return role in (UserRole.ADMIN, UserRole.SUPERADMIN)


def can_delete_user(
    request: Request,
    target_role: UserRole,
    target_id: int,
) -> bool:
    actor_role: UserRole | None = get_role(request)
    actor_id: int | None = get_user_id(request)

    if actor_role is None:
        return False

    # can't delete yourself
    if actor_id == target_id:
        return False

    # nobody can delete superadmin account
    if target_role == UserRole.SUPERADMIN:
        return False

    # admin can't delete another admin
    if actor_role == UserRole.ADMIN and target_role == UserRole.ADMIN:
        return False

    return True
