from core.module_engine.base import BaseModule


class Module(BaseModule):
    name = "platform_admin"

    router = None
    models = []
    admin_views = []
    middlewares = []
    dependencies = []
    tasks = []
