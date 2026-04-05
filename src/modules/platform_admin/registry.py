from sqladmin import BaseView, ModelView

AdminViewType = type[ModelView] | type[BaseView]
_admin_views: list[AdminViewType] = []


def register_admin(view: AdminViewType) -> AdminViewType:
    _admin_views.append(view)
    return view


def get_admin_views() -> list[AdminViewType]:
    return _admin_views
