from sqladmin import BaseView, expose
from sqlalchemy import func, select, text
from starlette.requests import Request
from starlette.responses import Response

from core.database import async_session
from core.settings import get_settings
from modules import loaded_modules


class DashboardView(BaseView):
    name = "Dashboard"
    icon = "fa-solid fa-house"
    is_index = True

    @expose("/", methods=["GET"])
    async def index(self, request: Request) -> Response:
        settings = get_settings()

        # ===== DB health =====
        db_ok = False
        try:
            async with async_session() as session:
                await session.execute(text("SELECT 1"))
            db_ok = True
        except Exception:
            db_ok = False

        # ===== stats =====
        stats = {
            "modules": len(loaded_modules),
            "users": await self._count_users(),
            "tasks": "-",  # позже подключим celery inspect
        }

        context = {
            "request": request,
            "settings": settings,
            "stats": stats,
            "health": {
                "db": db_ok,
                "celery": settings.celery_enabled,
                "metrics": settings.prometheus_enabled,
            },
        }

        return await self.templates.TemplateResponse(request, "sqladmin/index.html", context)

    async def _count_users(self) -> int:
        try:
            from modules.users.models import User

            async with async_session() as session:
                result = await session.execute(select(func.count()).select_from(User))
                return result.scalar_one()
        except Exception:
            return 0
