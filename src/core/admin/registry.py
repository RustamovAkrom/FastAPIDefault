from sqladmin import ModelView

_admin_views: list[type[ModelView]] = []


def register_admin(view: type[ModelView]) -> type[ModelView]:
    _admin_views.append(view)
    return view


def get_admin_views() -> list[type[ModelView]]:
    return _admin_views
