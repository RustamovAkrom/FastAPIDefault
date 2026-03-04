from typing import Any

from fastapi import FastAPI, Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.responses import RedirectResponse, Response

from admin import load_all_models
from core.database import async_session, get_db_engine
from core.security import verify_password
from core.settings import get_settings
from db.models.user import User, UserRole

_admin_views: list[type[ModelView]] = []


class AdminAuth(AuthenticationBackend):
    def __init__(self) -> None:
        settings = get_settings()
        super().__init__(secret_key=settings.secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username_raw: Any = form.get("username")
        password_raw: Any = form.get("password")

        if not isinstance(username_raw, str) or not isinstance(password_raw, str):
            return False

        async with async_session() as session:
            result = await session.execute(select(User).where(User.username == username_raw))
            user: User | None = result.scalar_one_or_none()

            if user is None or not user.is_active or not verify_password(password_raw, user.password):
                return False

            request.session.update({"admin_user_id": user.id, "role": user.role})
        return True

    async def logout(self, request: Request) -> bool | Response:
        request.session.clear()
        return RedirectResponse(request.url_for("admin:login"), status_code=302)

    async def authenticate(self, request: Request) -> bool | Response:
        user_id = request.session.get("admin_user_id")
        if not isinstance(user_id, int):
            return False

        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user: User | None = result.scalar_one_or_none()

            if user is None or user.role not in (UserRole.ADMIN, UserRole.SUPERADMIN):
                return False
        return True


class BaseAdmin(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    page_size = 50
    column_searchable_list = []
    column_sortable_list = []


def register_admin(view: type[ModelView]) -> type[ModelView]:
    _admin_views.append(view)
    return view


def get_admin_views() -> list[type[ModelView]]:
    return _admin_views


def init_admin(app: FastAPI) -> FastAPI:
    engine = get_db_engine()
    admin = Admin(app, engine=engine, authentication_backend=AdminAuth())

    load_all_models()

    for view in get_admin_views():
        admin.add_view(view)

    return app
