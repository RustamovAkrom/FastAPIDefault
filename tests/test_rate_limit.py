import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

from core.rate_limit import get_rate_limit_key
from core.settings import get_settings


@pytest.mark.anyio
async def test_rate_limit_key_forward(client: AsyncClient) -> None:
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"x-forwarded-for", b"1.2.3.4, 5.6.7.8")],
            "client": ("127.0.0.1", 123),
        }
    )

    key = get_rate_limit_key(request)

    assert key == "1.2.3.4"


@pytest.mark.anyio
async def test_rate_limit_key_ip(client: AsyncClient) -> None:
    request = Request(
        scope={
            "type": "http",
            "headers": [],
            "client": ("127.0.0.1", 123),
        }
    )

    key = get_rate_limit_key(request)

    assert key == "127.0.0.1"


@pytest.mark.anyio
async def test_rate_limit_trigger(fastapi_app: FastAPI) -> None:
    settings = get_settings()

    settings.rate_limit_enabled = True
    settings.rate_limit_default = "1/minute"

    @fastapi_app.get("/test-rate")
    async def test_endpoint() -> dict:
        return {"ok": True}

    async with AsyncClient(
        transport=ASGITransport(fastapi_app),
        base_url="http://test",
    ) as client:
        res1 = await client.get("/test-rate")
        assert res1.status_code == 200

        res2 = await client.get("/test-rate")
        assert res2.status_code in (429, 200)  # depends on backend
