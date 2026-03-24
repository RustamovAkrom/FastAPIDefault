import pytest
from httpx import AsyncClient

from app import create_app
from core.settings import get_settings


@pytest.mark.anyio
async def test_app_home_endpoint(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200


def test_app_docs_enabled() -> None:
    settings = get_settings()
    settings.debug = True

    app = create_app()

    assert app.docs_url == "/docs"
    assert app.openapi_url == "/openapi.json"


def test_app_docs_disabled() -> None:
    settings = get_settings()
    settings.debug = False

    app = create_app()

    assert app.docs_url is None


def test_rate_limit_enabled() -> None:
    settings = get_settings()
    settings.rate_limit_enabled = True

    app = create_app()

    assert hasattr(app.state, "limiter")
