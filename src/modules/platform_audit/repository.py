from __future__ import annotations

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session

from .models import Audit


class AuditRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def create(self, payload: dict) -> None:
        self.session.add(Audit(**payload))

    async def list(self, *, limit: int, offset: int) -> list[Audit]:
        result = await self.session.execute(select(Audit).order_by(Audit.id.desc()).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def delete(self, audit_id: int) -> bool:
        result = await self.session.execute(delete(Audit).where(Audit.id == audit_id))
        return bool(result.rowcount)
