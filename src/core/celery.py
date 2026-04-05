from celery import Celery

from core.logger import configure_logger
from core.module_engine.registry import iter_modules
from core.settings import get_settings

logger = configure_logger()
settings = get_settings()

celery_app = Celery(
    "fastapi_default",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer=settings.celery_task_serializer,
    result_serializer=settings.celery_result_serializer,
    accept_content=settings.celery_accept_content,
    timezone=settings.celery_timezone,
    enable_utc=True,
)


def autodiscover_module_tasks() -> None:
    """
    Discover Celery tasks inside modules automatically.

    Looks for:
        modules.<module>.tasks
    """

    task_modules: list[str] = []

    for module_name in iter_modules():
        module_path = f"modules.{module_name}.tasks"
        task_modules.append(module_path)

    if not task_modules:
        logger.debug("No module tasks discovered")
        return

    logger.info("Registering celery tasks", modules=task_modules)

    celery_app.autodiscover_tasks(task_modules)


# Run autodiscovery on import
autodiscover_module_tasks()
