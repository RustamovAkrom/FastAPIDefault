from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

SENSITIVE_FIELDS = {"password", "token", "authorization", "secret", "access_token", "refresh_token"}
MAX_BODY_SIZE = 1024  # 1KB


def sanitize(data: Any) -> Any:
    if isinstance(data, Mapping):
        return {str(k): ("***" if str(k).lower() in SENSITIVE_FIELDS else sanitize(v)) for k, v in data.items()}
    if isinstance(data, list):
        return [sanitize(item) for item in data]
    return data


def safe_parse_body(body: bytes) -> dict[str, Any] | list[Any] | None:
    if not body:
        return None

    if len(body) > MAX_BODY_SIZE:
        return {"truncated": True}

    try:
        parsed = json.loads(body)
        return sanitize(parsed)
    except Exception:
        return {"raw": body.decode(errors="ignore")}
