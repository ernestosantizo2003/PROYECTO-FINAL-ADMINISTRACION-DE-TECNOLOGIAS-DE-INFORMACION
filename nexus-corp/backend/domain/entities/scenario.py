from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Scenario:
    id: UUID
    name: str
    description: str
    stock_level: int       # 0-100
    demand_level: str      # bajo | medio | alto
    risk_level: str        # bajo | medio | alto
    created_by: UUID
    created_at: datetime
