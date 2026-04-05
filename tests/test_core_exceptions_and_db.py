from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI, HTTPException, Request

from core.exceptions.base import APIException
from core.exceptions.handlers import register_exception_handlers
from db.dependencies import get_db_session


class _FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

    async def close(self) -> None:
        self.closed = True


class _FailingSession(_FakeSession):
    async def commit(self) -> None:
        raise RuntimeError("commit failed")


@pytest.mark.anyio
async def test_api_exception_handlers_paths() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/raise-api")
    async def raise_api() -> None:
        raise APIException(detail="boom", code="x", status_code=418, values={"a": 1})

    @app.get("/raise-http")
    async def raise_http() -> None:
        raise HTTPException(status_code=404, detail="missing")

    @app.get("/raise-unexpected")
    async def raise_unexpected() -> None:
        raise RuntimeError("oops")

    @app.get("/needs-int")
    async def needs_int(v: int) -> dict[str, int]:
        return {"v": v}

    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(transport=ASGITransport(app, raise_app_exceptions=False), base_url="http://test") as ac:
        api_resp = await ac.get("/raise-api")
        assert api_resp.status_code == 418
        assert api_resp.json()["code"] == "x"

        http_resp = await ac.get("/raise-http")
        assert http_resp.status_code == 404
        assert http_resp.json()["code"] == "http_error"

        val_resp = await ac.get("/needs-int?v=abc")
        assert val_resp.status_code == 422
        assert val_resp.json()["code"] == "validation_error"

        ok_resp = await ac.get("/needs-int?v=1")
        assert ok_resp.status_code == 200
        assert ok_resp.json()["v"] == 1

        err_resp = await ac.get("/raise-unexpected")
        assert err_resp.status_code == 500
        assert err_resp.json()["code"] == "internal_error"


def test_api_exception_base_customization() -> None:
    exc = APIException()
    assert exc.status_code == 400

    custom = APIException(detail="d", code="c", status_code=499, values={"x": 1})
    assert str(custom) == "d"
    assert custom.code == "c"
    assert custom.values["x"] == 1


@pytest.mark.anyio
async def test_db_dependency_commit_and_rollback(monkeypatch) -> None:
    session = _FakeSession()
    monkeypatch.setattr("db.dependencies.get_session_factory", lambda: (lambda: session))

    gen: AsyncGenerator = get_db_session(Request({"type": "http", "headers": [], "method": "GET", "path": "/"}))
    yielded = await gen.__anext__()
    assert yielded is session
    with pytest.raises(StopAsyncIteration):
        await gen.__anext__()
    assert session.committed and session.closed

    failing = _FailingSession()
    monkeypatch.setattr("db.dependencies.get_session_factory", lambda: (lambda: failing))
    gen2: AsyncGenerator = get_db_session(Request({"type": "http", "headers": [], "method": "GET", "path": "/"}))
    await gen2.__anext__()
    with pytest.raises(RuntimeError):
        await gen2.__anext__()
    assert failing.rolled_back and failing.closed
