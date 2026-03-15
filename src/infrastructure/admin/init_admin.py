from fastapi import FastAPI
from sqladmin import Admin

from modules import load_admin
from infrastructure.admin.auth import AdminAuth
from infrastructure.admin.registry import get_admin_views
from core.database import get_db_engine
from core.settings import get_settings


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

    load_admin()

    for view in get_admin_views():
        admin.add_view(view)

    return app
