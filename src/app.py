from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.router import api_router
from core.admin import init_admin
from core.exceptions import register_exception_handlers
from core.lifespan import lifespan
from core.logger import configure_logger
from core.monitoring import router as monitoring_router
from core.prometheus import MetricsMiddleware
from core.sentry import init_sentry
from core.settings import get_settings

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=BASE_DIR / "templates")


def create_app() -> FastAPI:
    """
    Create FastAPI application instance with middleware, routers, and exception handlers.
    """
    configure_logger()

    settings = get_settings()

    if settings.sentry_dsn:
        init_sentry()

    app = FastAPI(
        title=settings.app_title,
        root_path=settings.root_path,
        redoc_url="/redoc",
        default_response_class=ORJSONResponse,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    app.add_middleware(MetricsMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router=api_router, prefix=settings.api_v1_str)
    app.include_router(router=monitoring_router, tags=["Monitoring"])

    register_exception_handlers(app)

    # initialize optional admin panel
    init_admin(app)

    # Home page
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def home(request: Request) -> HTMLResponse:
        base_url = f"{request.url.scheme}://{request.headers.get('host')}"
        hostname = request.url.hostname

        return templates.TemplateResponse(
            "index.html", {"request": request, "base_url": base_url, "hostname": hostname}
        )

    # Static files
    app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

    return app
