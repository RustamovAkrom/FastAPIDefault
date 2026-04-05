from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from core.settings import get_settings

router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=settings.BASE_DIR / "templates")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request) -> HTMLResponse:
    base_url = str(request.base_url).rstrip("/")
    hostname = request.url.hostname

    return templates.TemplateResponse("index.html", {"request": request, "base_url": base_url, "hostname": hostname})
