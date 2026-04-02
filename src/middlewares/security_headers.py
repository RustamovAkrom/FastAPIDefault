"""
Security Headers Middleware

Добавляет HTTP security headers.

Зачем нужен:
- защита от XSS
- защита от clickjacking
- улучшение security score

Когда включать:
- production
- публичные API / сайты
"""

from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # requires HTTPS (включать только если сайт работает по HTTPS)
        # response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"

        # Content Security Policy (CSP) - базовая политика, разрешающая загрузку ресурсов только с того же домена
        # response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response
