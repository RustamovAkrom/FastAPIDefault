from uuid import uuid4

import pytest

from modules.dummy.repository import DummyRepository
from modules.dummy.router import get_dummy_models
from modules.dummy.schemas import _to_camel
from modules.platform_admin.auth import SimpleAdminAuth


class _FakeRequest:
    def __init__(self, form_data: dict[str, str] | None = None, session: dict | None = None) -> None:
        self._form_data = form_data or {}
        self.session = session or {}

    async def form(self) -> dict[str, str]:
        return self._form_data

    def url_for(self, name: str) -> str:
        assert name == "admin:login"
        return "/admin/login"


@pytest.mark.anyio
async def test_admin_auth_methods() -> None:
    auth = SimpleAdminAuth()
    auth.settings.admin_username = "u"
    test_admin_password = uuid4().hex
    auth.settings.admin_password = test_admin_password

    fail = _FakeRequest(form_data={"username": "u", "password": "bad"}, session={})
    assert await auth.login(fail) is False

    missing = _FakeRequest(form_data={}, session={})
    assert await auth.login(missing) is False

    ok = _FakeRequest(form_data={"username": "u", "password": test_admin_password}, session={"x": 1})
    assert await auth.login(ok) is True
    assert ok.session.get("admin") is True

    out = await auth.logout(ok)
    assert out.status_code == 302

    assert await auth.authenticate(_FakeRequest(session={"admin": True})) is True
    assert await auth.authenticate(_FakeRequest(session={})) is False


@pytest.mark.anyio
async def test_dummy_repository_filter_and_list(dbsession) -> None:
    repo = DummyRepository(dbsession)
    await repo.create("a")
    await repo.create("b")

    all_items = await repo.get_all_dummies(limit=10, offset=0)
    assert len(all_items) >= 2

    filtered = await repo.filter(name="a")
    assert len(filtered) == 1

    filtered_all = await repo.filter(name=None)
    assert len(filtered_all) >= 2


@pytest.mark.anyio
async def test_dummy_get_route_and_schema_coverage(client) -> None:
    await client.post("api/v1/dummy/", json={"name": "x"})
    resp = await client.get("api/v1/dummy/?limit=10&page=0")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.anyio
async def test_dummy_router_type_adapter_direct() -> None:
    class _Repo:
        async def get_all_dummies(self, limit: int, offset: int):
            assert limit == 5
            assert offset == 10
            return [{"id": 1, "name": "n"}]

    items = await get_dummy_models(limit=5, page=2, dummy_crud=_Repo())  # type: ignore[arg-type]
    assert items[0].id == 1
    assert items[0].name == "n"


def test_schema_to_camel_helper() -> None:
    assert _to_camel("first_name") == "firstName"
