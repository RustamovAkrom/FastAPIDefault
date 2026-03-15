from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware

from modules import load_routers
from infrastructure.admin.init_admin import init_admin
from core.exceptions.handlers import register_exception_handlers
from core.lifespan import lifespan
from core.logger import configure_logger
from core.observability.monitoring import router as monitoring_router
from core.observability.prometheus import MetricsMiddleware
from core.observability.sentry import init_sentry
from core.settings import get_settings
from middlewares import RequestIDMiddleware, SecurityHeadersMiddleware


def create_app() -> FastAPI:
    """
    Create FastAPI application instance with middleware, routers, and exception handlers.
    """
    configure_logger()

    settings = get_settings()
    api_router = load_routers()

    if settings.sentry_dsn:
        init_sentry()

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        root_path=settings.root_path,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        docs_url="/docs" if settings.debug else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    ### Middlewares ###
    if settings.prometheus_enabled:
        app.add_middleware(MetricsMiddleware)

    # CORS headers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Request ID & Security Headers
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    # GZip Compression
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # сжимать ответы больше 1kb
    )
    # Restrict allowed host headers
    if settings.allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts,
        )
    # Routers
    app.include_router(router=api_router, prefix=settings.api_v1_str)
    app.include_router(router=monitoring_router, tags=["Monitoring"])

    # Exception handlers
    register_exception_handlers(app)

    # initialize optional admin panel
    if settings.admin_enabled:
        init_admin(app)

    # Templates
    templates = Jinja2Templates(directory=settings.BASE_DIR / "templates")

    # Home page
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def home(request: Request) -> HTMLResponse:
        base_url = f"{request.url.scheme}://{request.headers.get('host')}"
        hostname = request.url.hostname

        return templates.TemplateResponse(
            "index.html", {"request": request, "base_url": base_url, "hostname": hostname}
        )

    # Static files
    static_dir = settings.BASE_DIR / settings.static_root
    if static_dir.exists():
        app.mount(settings.static_url, StaticFiles(directory=str(static_dir)), name=settings.static_root)

    # Media files
    media_dir = settings.BASE_DIR / settings.media_root
    if media_dir.exists():
        app.mount(settings.media_url, StaticFiles(directory=str(media_dir)), name=settings.media_root)

    return app
