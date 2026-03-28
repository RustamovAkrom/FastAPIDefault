import inspect
from collections.abc import Callable

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import Response

from core.settings import get_settings

settings = get_settings()


def get_rate_limit_key(request: Request) -> str:
    """
    Identify client.
    Priority:
    - X-Forwarded-For (proxy)
    - IP
    - user_id (if auth added later)
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return get_remote_address(request)


limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=settings.rate_limit_storage_url,
)


def rate_limit_dep() -> Callable:
    return limiter.limit(settings.rate_limit_default)


async def rate_limit_exceeded_handler(
    request: Request,
    exc: Exception,
) -> Response:
    if not isinstance(exc, RateLimitExceeded):
        raise exc

    rate_exc: RateLimitExceeded = exc
    result = _rate_limit_exceeded_handler(request, rate_exc)

    if inspect.isawaitable(result):
        return await result

    return result
