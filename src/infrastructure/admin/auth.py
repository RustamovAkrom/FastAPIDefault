from fastapi import Request
from sqladmin.authentication import AuthenticationBackend
from starlette.responses import RedirectResponse, Response

from core.settings import get_settings


class SimpleAdminAuth(AuthenticationBackend):
    def __init__(self) -> None:
        settings = get_settings()
        super().__init__(secret_key=settings.secret_key)

        self.username = settings.admin_username
        self.password = settings.admin_password

    async def login(self, request: Request) -> bool:
        form = await request.form()

        username = form.get("username")
        password = form.get("password")

        if not isinstance(username, str) or not isinstance(password, str):
            return False

        if username == self.username and password == self.password:
            request.session.clear()
            request.session["admin"] = True
            return True

        return False

    async def logout(self, request: Request) -> bool | Response:
        request.session.clear()
        return RedirectResponse(url=request.url_for("admin:login"), status_code=302)

    async def authenticate(self, request: Request) -> bool | Response:
        return request.session.get("admin", False)
