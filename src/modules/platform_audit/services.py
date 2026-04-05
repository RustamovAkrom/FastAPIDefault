from __future__ import annotations

from core.database import get_session_factory

from .repository import AuditRepository


async def save_audit_log(payload: dict) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        repo = AuditRepository(session=session)
        try:
            await repo.create(payload)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
