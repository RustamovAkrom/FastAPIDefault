from fastapi import FastAPI
from sqladmin import Admin

from core.database import get_db_engine
from core.settings import get_settings
from infrastructure.admin.auth import AdminAuth
from infrastructure.admin.context import get_health, get_safe_settings, get_stats
from infrastructure.admin.registry import get_admin_views


def init_admin(app: FastAPI) -> FastAPI:
    settings = get_settings()
    engine = get_db_engine()

    admin = Admin(
        app,
        engine=engine,
        debug=settings.debug,
        title="FastAPI-Default Admin",
        authentication_backend=AdminAuth(),
        templates_dir="src/templates",
        logo_url="/static/images/fastapi.svg",
    )
    admin.templates.env.globals.update(
        settings=get_safe_settings(),
        stats=lambda: get_stats(),
        health=lambda: get_health(),
    )

    for view in get_admin_views():
        admin.add_view(view)

    return app
