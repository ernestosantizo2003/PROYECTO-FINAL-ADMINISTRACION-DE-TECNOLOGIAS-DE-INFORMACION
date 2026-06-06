from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from pydantic import BaseModel


class KPIResponse(BaseModel):
    id: UUID
    name: str
    value: float
    unit: str
    period: str
    category: str
    created_at: datetime

    model_config = {"from_attributes": True}


class KPIListResponse(BaseModel):
    kpis: List[KPIResponse]
    total: int


class DashboardResponse(BaseModel):
    total_rules: int
    total_scenarios: int
    total_decisions: int
    accepted_recommendations: int
    rejected_recommendations: int
    avg_satisfaction: float
    decisions_by_month: List[Dict[str, Any]]
    rules_by_category: List[Dict[str, Any]]
    feedback_distribution: List[Dict[str, Any]]
