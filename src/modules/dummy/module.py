from core.module_engine.base import BaseModule

from .admin import DummyAdmin

# Required import
from .models import Dummy
from .router import router


class Module(BaseModule):
    name = "dummy"

    router = router

    models = [Dummy]

    admin_views = [DummyAdmin]
