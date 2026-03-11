from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from core.security.types import TokenType
from core.settings import get_settings

settings = get_settings()


def _create_token(
    data: dict[str, Any],
    secret_key: str,
    expires_date: timedelta,
    token_type: str,
) -> str:
    """
    Internal JWT token generator.

    Args:
        data: payload data
        secret_key: JWT secret
        expires_delta: token lifetime
        token_type: access | refresh

    Returns:
        encoded JWT token
    """

    now = datetime.now(UTC)

    payload: dict[str, Any] = {
        **data,
        "type": token_type,
        "iat": now,
        "nbf": now,
        "exp": now + expires_date,
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(data: dict[str, Any]) -> str:
    """
    Generate access token
    """
    return _create_token(
        data=data,
        secret_key=settings.jwt_secret_key,
        expires_date=timedelta(minutes=settings.access_token_expire_minutes),
        token_type=TokenType.ACCESS,
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Generate refresh token
    """
    return _create_token(
        data=data,
        secret_key=settings.jwt_secret_key,
        expires_date=timedelta(minutes=settings.access_token_expire_minutes),
        token_type=TokenType.REFRESH,
    )
