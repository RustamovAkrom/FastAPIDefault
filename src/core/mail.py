from typing import Any, cast

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import SecretStr

from core.settings import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.smtp_user,
    MAIL_PASSWORD=SecretStr(settings.smtp_password),
    MAIL_FROM=settings.smtp_from_email,
    MAIL_PORT=settings.smtp_port,
    MAIL_SERVER=settings.smpt_host,
    MAIL_FROM_NAME=settings.smtp_from_name,
    MAIL_STARTTLS=settings.smtp_starttls,
    MAIL_SSL_TLS=settings.smtp_ssl,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_email(
    subject: str,
    recipients: list[str],
    body: str,
) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=cast(list[Any], recipients),
        body=body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)

    await fm.send_message(message)
