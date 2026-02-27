from fastapi import FastAPI
from sqladmin import Admin, ModelView

from admin.auth import AdminAuth
from core.database import get_db_engine
from admin import load_all_models


_admin_views: list[type[ModelView]] = []


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
    # load all admin models
    load_all_models()

    # register all admins
    for view in get_admin_views():
        admin.add_view(view)

    return app
