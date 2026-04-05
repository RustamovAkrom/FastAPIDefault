import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_dummy_validation_error(client: AsyncClient) -> None:
    resp = await client.post("api/v1/dummy/", json={})
    assert resp.status_code == 422
