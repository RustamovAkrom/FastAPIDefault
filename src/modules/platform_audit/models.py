from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Audit(Base):
    """HTTP audit log entry."""

    __tablename__ = "audits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # request
    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(500))
    query_params: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    request_body: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # response
    status_code: Mapped[int] = mapped_column(Integer)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)

    # client info
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    forwarded_for: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # tracing
    request_id: Mapped[str] = mapped_column(String(36), index=True)

    # timing/security
    latency_ms: Mapped[int] = mapped_column(Integer)
    is_suspicious: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
