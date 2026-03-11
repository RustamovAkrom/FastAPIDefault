from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.responses import RedirectResponse, Response

from core.database import async_session
from core.security import verify_password
from core.settings import get_settings
from db.models.user import User, UserRole


class AdminAuth(AuthenticationBackend):
    def __init__(self) -> None:
        settings = get_settings()
        super().__init__(secret_key=settings.secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()

        username_raw: object | None = form.get("username")
        password_raw: object | None = form.get("password")

        if not isinstance(username_raw, str):
            return False

        if not isinstance(password_raw, str):
            return False

        async with async_session() as session:
            result = await session.execute(select(User).where(User.username == username_raw))

            user: User | None = result.scalar_one_or_none()

            if user is None:
                return False

            if not user.is_active:
                return False

            if not verify_password(password_raw, user.password):
                return False

            request.session.update(
                {
                    "admin_user_id": user.id,
                    "role": user.role.value,
                }
            )

        return True

    async def logout(self, request: Request) -> bool | Response:
        request.session.clear()

        return RedirectResponse(
            url=request.url_for("admin:login"),
            status_code=302,
        )

    async def authenticate(self, request: Request) -> bool | Response:
        role_raw: object | None = request.session.get("role")

        if not isinstance(role_raw, str):
            return False

        try:
            role: UserRole = UserRole(role_raw)
        except ValueError:
            return False

        if role not in {UserRole.ADMIN, UserRole.SUPERADMIN}:
            return False

        return True
