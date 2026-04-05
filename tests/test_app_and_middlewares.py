import types

import pytest
from fastapi import FastAPI
from fastapi.responses import Response
from starlette.requests import Request as StarletteRequest

import app as app_module
from core.settings import Settings
from middlewares.metrics import MetricsMiddleware


@pytest.mark.anyio
async def test_metrics_middleware_branches() -> None:
    mw = MetricsMiddleware(app=FastAPI())

    req_metrics = StarletteRequest(
        {"type": "http", "headers": [], "client": ("1.1.1.1", 1), "method": "GET", "path": "/metrics", "scheme": "http"}
    )

    async def _ok(_r):
        return Response(status_code=200)

    resp_metrics = await mw.dispatch(req_metrics, _ok)
    assert resp_metrics.status_code == 200

    req_ok = StarletteRequest(
        {"type": "http", "headers": [], "client": ("1.1.1.1", 1), "method": "GET", "path": "/x", "scheme": "http"}
    )
    req_ok.scope["route"] = types.SimpleNamespace(path="/templated")

    async def _not_found(_r):
        return Response(status_code=404)

    resp_ok = await mw.dispatch(req_ok, _not_found)
    assert resp_ok.status_code == 404

    async def _boom(_r):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await mw.dispatch(req_ok, _boom)


def test_app_factory_and_configurators(monkeypatch, tmp_path) -> None:
    settings = Settings(
        env="test",
        debug=True,
        prometheus_enabled=True,
        rate_limit_enabled=True,
        sentry_enabled=True,
        sentry_dsn="dsn",
        admin_enabled=True,
    )
    settings.BASE_DIR = tmp_path
    (tmp_path / "static").mkdir()
    (tmp_path / "media").mkdir()

    monkeypatch.setattr(app_module, "configure_logger", lambda: None)
    called = {"sentry": 0, "admin": 0}
    monkeypatch.setattr(app_module, "init_sentry", lambda: called.__setitem__("sentry", called["sentry"] + 1))
    monkeypatch.setattr(app_module, "init_admin", lambda _app: called.__setitem__("admin", called["admin"] + 1))

    app = app_module.create_app(settings)
    assert app is not None
    assert called["sentry"] == 1
    assert called["admin"] == 1

    settings2 = Settings(env="test", debug=False, sentry_enabled=True, sentry_dsn=None, admin_enabled=False)
    app2 = app_module.create_app(settings2)
    assert app2 is not None
