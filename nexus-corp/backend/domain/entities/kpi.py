from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class KPI:
    id: UUID
    name: str
    value: float
    unit: str
    period: str
    category: str
    created_at: datetime
