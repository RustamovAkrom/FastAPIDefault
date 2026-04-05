from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    method: str
    path: str
    query_params: dict | None = None
    request_body: dict | None = None
    status_code: int
    response_body: str | None = None
    ip: str | None = None
    user_agent: str | None = None
    forwarded_for: str | None = None
    request_id: str
    latency_ms: int
    is_suspicious: int = Field(default=0)
    created_at: datetime
