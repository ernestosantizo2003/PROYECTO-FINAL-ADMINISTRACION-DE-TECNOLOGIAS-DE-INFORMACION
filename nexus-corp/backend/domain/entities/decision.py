from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class Decision:
    id: UUID
    scenario_id: UUID
    recommendations: List[dict]  # list of recommendation summaries
    rules_fired: List[UUID]
    status: str   # pendiente | aceptada | rechazada
    notes: Optional[str]
    created_by: UUID
    created_at: datetime
