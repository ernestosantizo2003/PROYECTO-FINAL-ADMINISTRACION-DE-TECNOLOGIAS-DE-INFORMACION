from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class Feedback:
    id: UUID
    decision_id: UUID
    user_id: UUID
    rating: int   # 1-5
    comment: Optional[str]
    created_at: datetime
