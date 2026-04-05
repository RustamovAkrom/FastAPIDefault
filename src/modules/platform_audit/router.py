from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import TypeAdapter

from .repository import AuditRepository
from .schemas import AuditSchema

router = APIRouter(prefix="/api/v1/audits", tags=["audit"])


@router.get("/", summary="Get audit logs")
async def list_audits(
    repo: Annotated[AuditRepository, Depends()],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    page: Annotated[int, Query(ge=0)] = 0,
) -> list[AuditSchema]:
    rows = await repo.list(limit=limit, offset=page * limit)
    adapter = TypeAdapter(list[AuditSchema])
    return adapter.validate_python(rows)


@router.delete("/{audit_id}", summary="Delete audit log")
async def delete_audit(
    audit_id: int,
    repo: Annotated[AuditRepository, Depends()],
) -> dict[str, str]:
    deleted = await repo.delete(audit_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return {"detail": "Audit log deleted"}
