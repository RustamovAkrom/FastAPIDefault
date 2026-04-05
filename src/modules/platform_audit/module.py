from core.module_engine.base import BaseModule

from .middlewares import AuditMiddleware
from .models import Audit
from .router import router


class Module(BaseModule):
    name = "platform_audit"

    router = router

    models = (Audit,)

    admin_views = ()

    middlewares = ((AuditMiddleware, {}),)
    dependencies = ()
    tasks = ()
