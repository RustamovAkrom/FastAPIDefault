from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import AsyncHTTPTransport

import app as app_module
from core import requests as core_requests
from core.logger import configure_logger
from core.observability import monitoring, prometheus, sentry
from core.settings import Settings


@pytest.mark.anyio
async def test_home_and_monitoring_endpoints(client) -> None:
    home = await client.get("/")
    assert home.status_code == 200

    health = await client.get("/healthcheck")
    assert health.status_code == 200
    assert "timestamp" in health.json()

    status = await client.get("/status")
    assert status.status_code == 200
    assert status.json()["app"] == "ok"


@pytest.mark.anyio
async def test_monitoring_version_and_metrics_key(monkeypatch, client) -> None:
    monkeypatch.setattr(monitoring, "version", lambda _: "9.9.9")
    version_resp = await client.get("/version")
    assert version_resp.status_code == 200
    assert version_resp.json()["version"] == "9.9.9"

    secure_settings = Settings(prometheus_metrics_key="secret", env="test")
    monkeypatch.setattr(monitoring, "get_settings", lambda: secure_settings)

    forbidden = await client.get("/metrics")
    assert forbidden.status_code == 403

    allowed = await client.get("/metrics", headers={"key": "secret"})
    assert allowed.status_code == 200


def test_sentry_helpers(monkeypatch) -> None:
    monkeypatch.setattr(sentry, "get_settings", lambda: Settings(env="test", sentry_dsn=None))
    sentry.init_sentry()

    called = {"ok": False}

    def _fake_init(**kwargs):
        called["ok"] = True
        assert kwargs["dsn"] == "dsn"

    monkeypatch.setattr(sentry.sentry_sdk, "init", _fake_init)
    monkeypatch.setattr(sentry, "get_settings", lambda: Settings(env="prod", sentry_dsn="dsn", debug=False))
    sentry.init_sentry()
    assert called["ok"]


@pytest.mark.anyio
async def test_prometheus_endpoints_and_build_registry(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("PROMETHEUS_MULTIPROC_DIR", str(tmp_path))
    reg = prometheus._build_registry()
    assert reg is not None

    resp = await prometheus.metrics_endpoint()
    assert resp.status_code == 200


def test_get_http_transport_cached() -> None:
    t1 = core_requests.get_http_transport()
    t2 = core_requests.get_http_transport()
    assert isinstance(t1, AsyncHTTPTransport)
    assert t1 is t2


def test_configure_logger_with_and_without_file_logging(monkeypatch, tmp_path) -> None:
    class _S:
        debug = False
        LOG_PATH = str(tmp_path / "logs")

    monkeypatch.setattr("core.logger.get_settings", lambda: _S())
    lg = configure_logger()
    assert lg is not None

    class _Bad:
        debug = False
        LOG_PATH = str(tmp_path / "readonly")

    monkeypatch.setattr("core.logger.get_settings", lambda: _Bad())

    def _raise(*args, **kwargs):
        raise OSError("readonly")

    monkeypatch.setattr("pathlib.Path.mkdir", _raise)
    lg2 = configure_logger()
    assert lg2 is not None


def test_configure_swagger_debug_toggle(monkeypatch) -> None:
    app = FastAPI(title="X", openapi_url="/openapi.json", docs_url=None, redoc_url=None)
    from core import swagger

    monkeypatch.setattr(swagger, "get_settings", lambda: Settings(debug=False, env="test"))
    swagger.configure_swagger(app)
    assert not any(route.path == "/docs" for route in app.routes)

    app2 = FastAPI(title="X", openapi_url="/openapi.json", docs_url=None, redoc_url=None)
    monkeypatch.setattr(swagger, "get_settings", lambda: Settings(debug=True, env="test"))
    swagger.configure_swagger(app2)
    paths = {route.path for route in app2.routes}
    assert "/docs" in paths
    assert "/redoc" in paths


@pytest.mark.anyio
async def test_swagger_routes_execute_and_settings_properties(monkeypatch) -> None:
    from httpx import ASGITransport, AsyncClient

    from core import swagger

    monkeypatch.setattr(swagger, "get_settings", lambda: Settings(env="test", debug=True))
    app = app_module.create_app(Settings(env="test", debug=True))
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        docs = await client.get("/docs")
        assert docs.status_code == 200
        redoc = await client.get("/redoc")
        assert redoc.status_code == 200
        oauth = await client.get("/docs/oauth2-redirect")
        assert oauth.status_code == 200

    test_db_password = uuid4().hex
    s_prod = Settings(env="prod", postgres_db="db", postgres_password=test_db_password)
    assert s_prod.is_prod is True
    assert s_prod.is_local is False
    assert "+asyncpg" not in s_prod.postgres_sync_url

    s_local = Settings(env="local")
    assert s_local.is_local is True

    monkeypatch.setattr(monitoring, "get_settings", lambda: Settings(env="test", prometheus_metrics_key=None))
    assert monitoring._verify_metrics_key() is None
