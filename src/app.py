from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from core.exceptions.handlers import register_exception_handlers
from core.lifespan import lifespan
from core.logger import configure_logger
from core.observability.monitoring import router as monitoring_router
from core.observability.sentry import init_sentry
from core.rate_limit import limiter, rate_limit_exceeded_handler  # , rate_limit_dep
from core.settings import Settings, get_settings
from infrastructure.admin.init_admin import init_admin
from middlewares import RequestIDMiddleware, SecurityHeadersMiddleware
from middlewares.metrics import MetricsMiddleware
from modules import load_modules


### CONFIGURATORS ###
def configure_middlewares(app: FastAPI, settings: Settings) -> None:
    # Security
    if settings.allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )
    # Session (Critical)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="admin_session",
        max_age=60 * 60 * 24,  # 1 day
        same_site="lax",
        https_only=not settings.debug,  # secure in prod
    )
    # Observability
    if settings.prometheus_enabled:
        app.add_middleware(MetricsMiddleware)

    # Rate limiter
    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)

    # Request tracking
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Compression
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # сжимать ответы больше 1kb
    )


### ROUTES ###
def configure_routes(app: FastAPI, settings: Settings) -> None:
    api_router = load_modules()

    app.include_router(
        router=api_router,
        prefix=settings.api_v1_str,
        # dependencies=[Depends(rate_limit_dep)] # rate limit dependencies
    )
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


### TEMPLATES ###
def configure_templates(app: FastAPI, settings: Settings) -> None:
    templates = Jinja2Templates(directory=settings.BASE_DIR / "templates")

    # Default home page
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def home(request: Request) -> HTMLResponse:
        base_url = f"{request.url.scheme}://{request.headers.get('host')}"
        hostname = request.url.hostname

        return templates.TemplateResponse(
            "index.html", {"request": request, "base_url": base_url, "hostname": hostname}
        )


### OBSERVABILITY ###
def configure_observability(settings: Settings) -> None:
    if settings.sentry_enabled and settings.sentry_dsn:
        init_sentry()


### FACTORY ###
def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    configure_logger()
    configure_observability(settings)

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        description=settings.app_description,
        root_path=settings.root_path,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    configure_middlewares(app, settings)
    configure_routes(app, settings)
    configure_admin_panel(app, settings)
    configure_static_files(app, settings)
    configure_templates(app, settings)

    register_exception_handlers(app)

    return app
