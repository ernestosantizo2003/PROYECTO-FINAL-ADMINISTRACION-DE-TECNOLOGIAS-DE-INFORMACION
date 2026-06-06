from dataclasses import dataclass, field
from typing import List
from uuid import UUID


@dataclass
class Role:
    id: UUID
    name: str  # admin_sistema | admin_conocimiento | decisor | analista
    description: str
    permissions: List[str] = field(default_factory=list)
