from fastapi import FastAPI
from sqladmin import Admin

from admin import load_all_models
from core.admin.auth import AdminAuth
from core.admin.registry import get_admin_views
from core.database import get_db_engine


def init_admin(app: FastAPI) -> FastAPI:
    engine = get_db_engine()

    admin = Admin(
        app,
        engine=engine,
        authentication_backend=AdminAuth(),
    )

    load_all_models()

    for view in get_admin_views():
        admin.add_view(view)

    return app
