from sqladmin import ModelView


class BaseAdmin(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    page_size = 50

    column_searchable_list = []
    column_sortable_list = []
