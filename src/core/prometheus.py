from __future__ import annotations

import os
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
    multiprocess,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from core.settings import get_settings

settings = get_settings()
APP_NAME = settings.app_name


# =========================================================
# MULTIPROCESS REGISTRY (FOR UVICORN WORKERS / DOCKER)
# =========================================================


def _build_registry() -> CollectorRegistry:
    """
    If running with multiple workers (uvicorn/gunicorn),
    use Prometheus multiprocess registry.
    """
    if os.getenv("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)  # type: ignore[no-untyped-call]
        return registry

    return CollectorRegistry()


REGISTRY = _build_registry()


# =========================================================
# METRICS (GLOBAL SINGLETONS)
# IMPORTANT: NEVER create metrics inside functions!
# =========================================================

REQUEST_TOTAL = Counter(
    f"{APP_NAME}_requests_total",
    "Total HTTP requests",
    ["app", "method", "endpoint", "status"],
    registry=REGISTRY,
)

REQUEST_DURATION = Histogram(
    f"{APP_NAME}_request_duration_seconds",
    "HTTP request duration",
    ["app", "method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
    registry=REGISTRY,
)

REQUEST_ERRORS = Counter(
    f"{APP_NAME}_request_errors_total",
    "Total HTTP error responses",
    ["app", "method", "endpoint", "status"],
    registry=REGISTRY,
)

EXCEPTIONS_TOTAL = Counter(
    f"{APP_NAME}_exceptions_total",
    "Total unhandled exceptions",
    ["app", "endpoint"],
    registry=REGISTRY,
)

IN_PROGRESS = Gauge(
    f"{APP_NAME}_requests_in_progress",
    "Requests currently in progress",
    ["app"],
    registry=REGISTRY,
)

APP_INFO = Info(
    f"{APP_NAME}_app",
    "Application information",
    registry=REGISTRY,
)

APP_INFO.info(
    {
        "version": settings.app_version,
        "environment": settings.env,
    }
)


# =========================================================
# METRICS ENDPOINT (/metrics)
# =========================================================


async def metrics_endpoint() -> StarletteResponse:
    """
    Prometheus scrape endpoint.
    """
    data = generate_latest(REGISTRY)
    return StarletteResponse(data, media_type=CONTENT_TYPE_LATEST)


# =========================================================
# MIDDLEWARE
# =========================================================


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Production-ready Prometheus middleware.

    Captures:
    - total requests
    - latency
    - errors
    - exceptions
    - in-progress requests
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # ignore non-API + metrics endpoint
        if request.url.path.startswith("/metrics"):
            return await call_next(request)

        app_label = APP_NAME
        method = request.method

        route = request.scope.get("route")
        endpoint = route.path if route else request.url.path

        start_time = time.perf_counter()

        IN_PROGRESS.labels(app=app_label).inc()

        try:
            response = await call_next(request)
            status = str(response.status_code)

        except Exception:
            # exceptions metric
            EXCEPTIONS_TOTAL.labels(
                app=app_label,
                endpoint=endpoint,
            ).inc()

            REQUEST_ERRORS.labels(
                app=app_label,
                method=method,
                endpoint=endpoint,
                status="500",
            ).inc()

            IN_PROGRESS.labels(app=app_label).dec()
            raise

        duration = time.perf_counter() - start_time

        REQUEST_TOTAL.labels(
            app=app_label,
            method=method,
            endpoint=endpoint,
            status=status,
        ).inc()

        REQUEST_DURATION.labels(
            app=app_label,
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        if response.status_code >= 400:
            REQUEST_ERRORS.labels(
                app=app_label,
                method=method,
                endpoint=endpoint,
                status=status,
            ).inc()

        IN_PROGRESS.labels(app=app_label).dec()

        return response
