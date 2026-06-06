from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID


@dataclass
class AuditLog:
    id: UUID
    user_id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    details: Dict[str, Any]
    ip_address: Optional[str]
    created_at: datetime
