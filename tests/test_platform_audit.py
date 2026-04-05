import pytest
from httpx import AsyncClient

from modules.platform_audit.security import safe_parse_body, sanitize


def test_audit_security_helpers() -> None:
    masked = "*" * 3
    data = {"username": "john", "password": "secret", "nested": {"token": "x"}}
    cleaned = sanitize(data)
    assert cleaned["password"] == masked
    assert cleaned["nested"]["token"] == masked

    assert safe_parse_body(b"") is None
    assert safe_parse_body(b'{"password":"123"}') == {"password": "***"}
    assert safe_parse_body(b"not-json") == {"raw": "not-json"}


@pytest.mark.anyio
async def test_audit_routes_and_middleware(client: AsyncClient) -> None:
    # trigger middleware by calling business endpoint
    resp = await client.post("/api/v1/dummy/", json={"name": "audit-row"})
    assert resp.status_code == 201

    audits_resp = await client.get("/api/v1/audits/")
    assert audits_resp.status_code == 200
    audits = audits_resp.json()
    assert isinstance(audits, list)
    assert len(audits) >= 1

    audit_id = audits[0]["id"]
    del_resp = await client.delete(f"/api/v1/audits/{audit_id}")
    assert del_resp.status_code == 200

    missing_resp = await client.delete("/api/v1/audits/999999")
    assert missing_resp.status_code == 404
