from fastapi import FastAPI
from sqladmin import Admin

from core.database import get_db_engine
from core.settings import get_settings
from infrastructure.admin.auth import SimpleAdminAuth
from infrastructure.admin.registry import get_admin_views


def init_admin(app: FastAPI) -> FastAPI:
    settings = get_settings()
    engine = get_db_engine()

    admin = Admin(
        app,
        engine=engine,
        debug=settings.debug,
        title="FastAPI-Default Admin",
        authentication_backend=SimpleAdminAuth(),
        templates_dir="src/templates",
        logo_url="/static/images/fastapi.svg",
    )

    for view in get_admin_views():
        admin.add_view(view)

    return app
