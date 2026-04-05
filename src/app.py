from typing import Any, cast

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from core.exceptions.handlers import register_exception_handlers
from core.lifespan import lifespan
from core.logger import configure_logger
from core.module_engine.base import BaseModule
from core.module_engine.registry import get_loaded_modules, load_modules
from core.observability.monitoring import router as monitoring_router
from core.observability.sentry import init_sentry
from core.rate_limit import limiter, rate_limit_exceeded_handler  # , rate_limit_dep
from core.settings import Settings, get_settings
from core.swagger import configure_swagger
from middlewares import RequestIDMiddleware, SecurityHeadersMiddleware
from middlewares.logging import LoggingMiddleware
from middlewares.metrics import MetricsMiddleware
from modules.platform_admin.init_admin import init_admin


### CONFIGURATORS ###
def configure_middlewares(app: FastAPI, settings: Settings, modules: tuple[BaseModule, ...]) -> None:
    # Trusted hosts (security)
    if settings.allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts or ["*"],
        )

    # CORS (browser security)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    # Request ID (context)
    app.add_middleware(RequestIDMiddleware)

    # Logging (Observability)
    app.add_middleware(LoggingMiddleware)

    # Metrics (Observability)
    if settings.prometheus_enabled:
        app.add_middleware(MetricsMiddleware)

    # Rate Limit (protection)
    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)

    # Session (auth)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="admin_session",
        max_age=60 * 60 * 24,  # 1 day
        same_site="lax",
        https_only=not settings.debug,  # secure in prod
    )

    # Security Headers (response hardening)
    app.add_middleware(SecurityHeadersMiddleware)

    # GZip (performance)
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # gzip responses larger than 1KB
    )

    # Module middlewares (loaded from module engine)
    for module in modules:
        for middleware_cls, options in module.middlewares:
            app.add_middleware(cast(Any, middleware_cls), **options)


### ROUTES ###
def configure_routes(app: FastAPI, api_router: APIRouter) -> None:
    # load all module routes
    app.include_router(
        router=api_router,
        # dependencies=[Depends(rate_limit_dep)] # rate limit dependencies
    )
    # monitoring routes (not rate limited)
    app.include_router(router=monitoring_router, tags=["Monitoring"])


### ADMIN ###
def configure_admin_panel(app: FastAPI, settings: Settings) -> None:
    if settings.admin_enabled:
        init_admin(app)


### STATIC & MEDIA ###
def configure_static_files(app: FastAPI, settings: Settings) -> None:
    static_dir = settings.BASE_DIR / settings.static_root
    if static_dir.exists():
        app.mount(settings.static_url, StaticFiles(directory=str(static_dir)), name=settings.static_root)

    media_dir = settings.BASE_DIR / settings.media_root
    if media_dir.exists():
        app.mount(settings.media_url, StaticFiles(directory=str(media_dir)), name=settings.media_root)


### OBSERVABILITY ###
def configure_observability(settings: Settings) -> None:
    if settings.sentry_enabled and settings.sentry_dsn:
        init_sentry()


### FACTORY ###
def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    configure_logger()
    configure_observability(settings)

    api_router = load_modules()
    modules = get_loaded_modules()

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=settings.app_description,
        root_path=settings.root_path,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    configure_swagger(app)
    configure_middlewares(app, settings, modules)
    configure_routes(app, api_router)
    configure_admin_panel(app, settings)
    configure_static_files(app, settings)

    register_exception_handlers(app)

    return app
