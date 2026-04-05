from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from core.logger import configure_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        logger = configure_logger()
        response = await call_next(request)

        logger.info(
            "request",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

        return response
