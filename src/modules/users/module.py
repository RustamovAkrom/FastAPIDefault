from modules.base import BaseModule

from .admin import UserAdmin

# важно: импорт моделей
from .models import User
from .router import router


class Module(BaseModule):
    name = "users"

    router = router

    models = [User]

    admin_views = [UserAdmin]
