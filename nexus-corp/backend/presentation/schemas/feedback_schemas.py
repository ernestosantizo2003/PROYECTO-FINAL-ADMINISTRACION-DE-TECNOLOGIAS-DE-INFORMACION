from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class FeedbackCreateRequest(BaseModel):
    decision_id: UUID
    rating: int
    comment: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if not (1 <= v <= 5):
            raise ValueError("El rating debe estar entre 1 y 5")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "decision_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "rating": 4,
                "comment": "Muy buenas recomendaciones, las aplicamos de inmediato",
            }
        }
    }


class FeedbackResponse(BaseModel):
    id: UUID
    decision_id: UUID
    user_id: UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackListResponse(BaseModel):
    items: List[FeedbackResponse]
    total: int
    page: int = 0
    size: int = 50


class FeedbackStatsResponse(BaseModel):
    average_rating: float
    total_count: int
    distribution: List[Dict[str, Any]]
