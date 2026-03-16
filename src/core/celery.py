from celery import Celery

from core.settings import get_settings

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

# celery_app.autodiscover_tasks(["tasks"])
