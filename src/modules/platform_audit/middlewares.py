from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .security import safe_parse_body
from .services import save_audit_log


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = time.perf_counter()
        request_id = str(uuid.uuid4())

        forwarded_for = request.headers.get("x-forwarded-for")
        ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else None)

        raw_body = await request.body()
        parsed_body = safe_parse_body(raw_body)

        response = await call_next(request)
        latency_ms = int((time.perf_counter() - started) * 1000)

        payload = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "request_body": parsed_body,
            "status_code": response.status_code,
            "response_body": None,
            "ip": ip,
            "user_agent": request.headers.get("user-agent"),
            "forwarded_for": forwarded_for,
            "request_id": request_id,
            "latency_ms": latency_ms,
            "is_suspicious": 1 if response.status_code >= 500 else 0,
        }

        asyncio.create_task(save_audit_log(payload))
        return response
