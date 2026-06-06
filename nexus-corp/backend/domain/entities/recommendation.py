from dataclasses import dataclass
from uuid import UUID


@dataclass
class Recommendation:
    id: UUID
    decision_id: UUID
    rule_id: UUID
    text: str
    priority: int
    justification: str
    is_accepted: bool
