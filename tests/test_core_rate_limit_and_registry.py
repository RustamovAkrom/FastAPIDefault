import types

import pytest
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import ValidationError
from starlette.requests import Request as StarletteRequest

from core import rate_limit
from core.lifespan import lifespan
from core.module_engine.base import BaseModule, ModuleSpec
from core.module_engine.registry import (
    ModuleDependencyError,
    ModuleRegistryError,
    get_loaded_modules,
    load_modules,
    sort_modules,
)


def test_rate_limit_key_and_handler(monkeypatch) -> None:
    scope = {
        "type": "http",
        "headers": [(b"x-forwarded-for", b"8.8.8.8")],
        "client": ("10.0.0.10", 1234),
        "method": "GET",
        "path": "/",
    }
    req = StarletteRequest(scope)
    from core.settings import Settings

    settings = Settings(trusted_proxies=["10.0.0.10"], env="test")
    monkeypatch.setattr(rate_limit, "get_settings", lambda: settings)
    assert rate_limit.get_rate_limit_key(req) == "8.8.8.8"

    scope2 = {"type": "http", "headers": [], "client": ("1.2.3.4", 1111), "method": "GET", "path": "/"}
    req2 = StarletteRequest(scope2)
    assert rate_limit.get_rate_limit_key(req2) == "1.2.3.4"
    assert callable(rate_limit.rate_limit_dep())


@pytest.mark.anyio
async def test_rate_limit_exceeded_handler(monkeypatch) -> None:
    req = StarletteRequest({"type": "http", "headers": [], "client": ("1.1.1.1", 1), "method": "GET", "path": "/"})

    class _RL(rate_limit.RateLimitExceeded):
        pass

    class _Limit:
        error_message = "limit"

    exc = _RL(_Limit())

    async def _awaitable_handler(_request, _exc):
        return Response(status_code=429)

    monkeypatch.setattr(rate_limit, "_rate_limit_exceeded_handler", _awaitable_handler)
    r = await rate_limit.rate_limit_exceeded_handler(req, exc)
    assert r.status_code == 429

    monkeypatch.setattr(rate_limit, "_rate_limit_exceeded_handler", lambda _request, _exc: Response(status_code=429))
    r2 = await rate_limit.rate_limit_exceeded_handler(req, exc)
    assert r2.status_code == 429

    with pytest.raises(RuntimeError):
        await rate_limit.rate_limit_exceeded_handler(req, RuntimeError("x"))


def test_sort_modules_errors_and_order() -> None:
    class A(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="a", dependencies=[])

    class B(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="b", dependencies=["a"])

    ordered = sort_modules([B(), A()])
    assert [m.spec.name for m in ordered] == ["a", "b"]

    class Unknown(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="u", dependencies=["missing"])

    with pytest.raises(ModuleDependencyError):
        sort_modules([Unknown()])

    class C1(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="c1", dependencies=["c2"])

    class C2(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="c2", dependencies=["c1"])

    with pytest.raises(ModuleDependencyError):
        sort_modules([C1(), C2()])


def test_load_modules_branches(monkeypatch) -> None:
    from core.module_engine import registry

    class Good(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="good", dependencies=[])

        def startup(self) -> None:
            return None

    class BadStartup(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="bad_startup", dependencies=[])

        def startup(self) -> None:
            raise RuntimeError("fail")

    class InvalidSpec(BaseModule):
        @property
        def spec(self) -> ModuleSpec:  # type: ignore[override]
            raise ValidationError.from_exception_data("x", [])

    class NoModuleClass:
        pass

    class InitFails(BaseModule):
        def __init__(self) -> None:
            raise RuntimeError("init fail")

        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="init", dependencies=[])

    assert InitFails.spec.fget(InitFails.__new__(InitFails)).name == "init"

    fake_modules = ["import_fail", "invalid_class", "init_fail", "invalid_spec", "good", "duplicate", "bad_startup"]
    monkeypatch.setattr(registry, "iter_modules", lambda: iter(fake_modules))

    def fake_import(path: str):
        name = path.split(".")[-2]
        if name == "import_fail":
            raise RuntimeError("import")
        if name == "invalid_class":
            return types.SimpleNamespace(Module=NoModuleClass)
        if name == "init_fail":
            return types.SimpleNamespace(Module=InitFails)
        if name == "invalid_spec":
            return types.SimpleNamespace(Module=InvalidSpec)
        if name == "good":
            return types.SimpleNamespace(Module=Good)
        if name == "duplicate":
            class Duplicate(Good):
                @property
                def spec(self) -> ModuleSpec:
                    return ModuleSpec(name="good", dependencies=[])

            return types.SimpleNamespace(Module=Duplicate)
        if name == "bad_startup":
            return types.SimpleNamespace(Module=BadStartup)
        raise AssertionError(name)

    monkeypatch.setattr(registry.importlib, "import_module", fake_import)
    monkeypatch.setattr(registry, "register_admin", lambda view: None)
    with pytest.raises(AssertionError):
        fake_import("modules.unknown.module")

    with pytest.raises(ModuleRegistryError):
        load_modules()

    monkeypatch.setattr(registry, "iter_modules", lambda: iter(["good"]))
    router = load_modules()
    assert router is not None
    assert [m.spec.name for m in get_loaded_modules()] == ["good"]


def test_load_modules_dependency_error_branch(monkeypatch) -> None:
    from core.module_engine import registry

    class MissingDep(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="x", dependencies=["nope"])

    monkeypatch.setattr(registry, "iter_modules", lambda: iter(["x"]))
    monkeypatch.setattr(registry.importlib, "import_module", lambda _path: types.SimpleNamespace(Module=MissingDep))
    with pytest.raises(ModuleDependencyError):
        load_modules()


def test_load_modules_register_admin_views(monkeypatch) -> None:
    from core.module_engine import registry

    class WithAdmin(BaseModule):
        @property
        def spec(self) -> ModuleSpec:
            return ModuleSpec(name="with_admin", dependencies=[])

        @property
        def admin_views(self) -> list[type]:
            class V:
                pass

            return [V]

    called = {"n": 0}
    monkeypatch.setattr(registry, "iter_modules", lambda: iter(["with_admin"]))
    monkeypatch.setattr(registry.importlib, "import_module", lambda _path: types.SimpleNamespace(Module=WithAdmin))
    monkeypatch.setattr(registry, "register_admin", lambda _view: called.__setitem__("n", called["n"] + 1))
    router = load_modules()
    assert router is not None
    assert called["n"] == 1


@pytest.mark.anyio
async def test_lifespan_shutdown(monkeypatch) -> None:
    class _Engine:
        def __init__(self) -> None:
            self.disposed = False

        async def dispose(self) -> None:
            self.disposed = True

    class _Transport:
        def __init__(self) -> None:
            self.closed = False

        async def aclose(self) -> None:
            self.closed = True

    class _Module:
        def __init__(self, fail: bool = False) -> None:
            self.fail = fail

        def shutdown(self) -> None:
            if self.fail:
                raise RuntimeError("x")

    engine = _Engine()
    transport = _Transport()

    monkeypatch.setattr("core.lifespan.get_db_engine", lambda: engine)
    monkeypatch.setattr("core.lifespan.get_http_transport", lambda: transport)
    monkeypatch.setattr("core.lifespan.loaded_modules", [_Module(True), _Module(False)])

    app = FastAPI()
    async with lifespan(app):
        pass

    assert engine.disposed and transport.closed
