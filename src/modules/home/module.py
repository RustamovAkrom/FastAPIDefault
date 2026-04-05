from core.module_engine.base import BaseModule

from .router import router


class Module(BaseModule):
    name = "home"

    router = router

    models = ()

    admin_views = ()

    middlewares = ()
    dependencies = ()
    tasks = ()
