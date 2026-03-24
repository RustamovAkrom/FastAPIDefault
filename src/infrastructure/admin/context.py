from sqlalchemy import func, select, text

from core.database import async_session
from core.settings import get_settings
from modules import loaded_modules


def get_safe_settings() -> dict:
    settings = get_settings()

    return {
        "env": settings.env,
        "debug": settings.debug,
        "app_name": settings.app_name,
        "app_version": settings.app_version,
    }


async def get_stats() -> dict:
    users_count = 0

    try:
        from modules.users.models import User

        async with async_session() as session:
            result = await session.execute(select(func.count()).select_from(User))
            users_count = result.scalar_one()

    except Exception:
        users_count = 0

    return {
        "modules": len(loaded_modules),
        "users": users_count,
        "tasks": "-",  # позже celery inspect
    }


async def get_health() -> dict:
    settings = get_settings()

    db_ok = False

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "db": db_ok,
        "celery": settings.celery_enabled,
        "metrics": settings.prometheus_enabled,
    }
