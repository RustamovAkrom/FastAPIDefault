import asyncio

from core.celery import celery_app
from core.mail import send_email


@celery_app.task  # type: ignore[misc]
def send_email_task(subject: str, recipients: list[str], body: str) -> None:
    """
    Celery expects regular sync callables by default.
    Run async mail sender inside a dedicated event loop.
    """
    asyncio.run(send_email(subject, recipients, body))
