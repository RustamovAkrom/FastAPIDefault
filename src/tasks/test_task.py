from core.celery import celery_app


@celery_app.task  # type: ignore[misc]
def test_task() -> str:
    print("CELERY WORKS")
    return "ok"
