import pytest
from httpx import AsyncClient

from core.settings import get_settings


@pytest.mark.anyio
async def test_create_dummy_model(
    client: AsyncClient,
) -> None:
    settings = get_settings()
    """Tests dummy instance creation."""
    test_name = "test_name"
    response = await client.post(
        f"{settings.api_v1_str}/dummy/",
        json={
            "name": test_name,
        },
    )
    assert response.status_code == 201
