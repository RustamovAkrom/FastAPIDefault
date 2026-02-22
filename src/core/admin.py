from fastapi import FastAPI
from sqladmin import Admin

from admin.auth import AdminAuth
from admin.loader import load_admin_modules
from admin.registry import get_admin_views
from core.database import get_db_engine


def init_admin(app: FastAPI) -> FastAPI:
    engine = get_db_engine()

    admin = Admin(app, engine=engine, authentication_backend=AdminAuth())
    # load all admin models
    load_admin_modules()

    # register all admins
    for view in get_admin_views():
        admin.add_view(view)

    return app
