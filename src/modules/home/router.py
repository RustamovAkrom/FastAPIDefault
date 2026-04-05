from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.templating import Jinja2Templates

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request) -> HTMLResponse:
    base_url = str(request.base_url).rstrip("/")
    hostname = request.url.hostname

    return templates.TemplateResponse("index.html", {"request": request, "base_url": base_url, "hostname": hostname})
