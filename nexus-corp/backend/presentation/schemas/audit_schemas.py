from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    skip: int
    limit: int
