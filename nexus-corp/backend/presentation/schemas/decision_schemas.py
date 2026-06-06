from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    scenario_id: Optional[UUID] = None
    name: Optional[str] = "Escenario What-If"
    description: Optional[str] = ""
    stock_level: int
    demand_level: Literal["bajo", "medio", "alto"]
    risk_level: Literal["bajo", "medio", "alto"]
    notes: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Análisis Q4",
                "description": "Escenario de crisis de inventario",
                "stock_level": 15,
                "demand_level": "alto",
                "risk_level": "medio",
                "notes": "Análisis urgente fin de trimestre",
            }
        }
    }


class DecisionStatusUpdateRequest(BaseModel):
    status: Literal["pendiente", "aceptada", "rechazada"]
    notes: Optional[str] = None


class DecisionResponse(BaseModel):
    id: UUID
    scenario_id: UUID
    recommendations: List[Dict[str, Any]]
    rules_fired: List[str]
    status: str
    notes: Optional[str] = None
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    id: UUID
    decision_id: UUID
    rule_id: UUID
    text: str
    priority: int
    justification: str
    is_accepted: bool

    model_config = {"from_attributes": True}


class DecisionWithRecommendationsResponse(BaseModel):
    decision: DecisionResponse
    recommendations: List[RecommendationResponse]


class DecisionListResponse(BaseModel):
    decisions: List[DecisionResponse]
    total: int
