from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID


@dataclass
class KnowledgeRule:
    id: UUID
    name: str
    description: str
    conditions: Dict[str, Any]  # JSON: {"stock_level": {"operator": "<", "value": 20}, ...}
    action: str
    priority: int  # 1=alta, 2=media, 3=baja
    category: str
    is_active: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime
