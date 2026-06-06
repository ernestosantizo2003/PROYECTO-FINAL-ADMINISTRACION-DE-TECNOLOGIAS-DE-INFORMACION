from typing import List
from uuid import UUID

from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    id: UUID
    decision_id: UUID
    rule_id: UUID
    text: str
    priority: int
    justification: str
    is_accepted: bool

    model_config = {"from_attributes": True}


class RecommendationListResponse(BaseModel):
    recommendations: List[RecommendationResponse]
