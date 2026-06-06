from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from datetime import datetime

from presentation.dependencies import get_audit_repo, require_role, CurrentUser
from presentation.schemas.audit_schemas import AuditLogListResponse, AuditLogResponse

router = APIRouter(prefix="/audit", tags=["Auditoría"])

ADMIN_ONLY = require_role("admin_sistema")


def _audit_to_response(log) -> AuditLogResponse:
    return AuditLogResponse(
        id=log.id,
        user_id=log.user_id,
        action=log.action,
        entity_type=log.entity_type,
        entity_id=log.entity_id,
        details=log.details,
        ip_address=log.ip_address,
        created_at=log.created_at,
    )


@router.get("/", response_model=AuditLogListResponse, summary="Listar registros de auditoría")
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: Optional[UUID] = Query(None),
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(ADMIN_ONLY),
    audit_repo=Depends(get_audit_repo),
):
    """List audit logs with optional filters."""
    logs = audit_repo.list_all(
        skip=skip,
        limit=limit,
        user_id=user_id,
        entity_type=entity_type,
        action=action,
    )
    total = audit_repo.count()
    return AuditLogListResponse(
        items=[_audit_to_response(l) for l in logs],
        total=total,
    )
