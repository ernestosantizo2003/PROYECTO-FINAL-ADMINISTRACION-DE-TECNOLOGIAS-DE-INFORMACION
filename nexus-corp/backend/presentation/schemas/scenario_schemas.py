from datetime import datetime
from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, field_validator


class ScenarioCreateRequest(BaseModel):
    name: str
    description: str = ""
    stock_level: int
    demand_level: Literal["bajo", "medio", "alto"]
    risk_level: Literal["bajo", "medio", "alto"]

    @field_validator("stock_level")
    @classmethod
    def validate_stock_level(cls, v: int) -> int:
        if not (0 <= v <= 100):
            raise ValueError("stock_level debe estar entre 0 y 100")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Escenario Q4 2024",
                "description": "Análisis de inventario para el cuarto trimestre",
                "stock_level": 15,
                "demand_level": "alto",
                "risk_level": "medio",
            }
        }
    }


class ScenarioResponse(BaseModel):
    id: UUID
    name: str
    description: str
    stock_level: int
    demand_level: str
    risk_level: str
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ScenarioListResponse(BaseModel):
    items: List[ScenarioResponse]
    total: int
    page: int = 0
    size: int = 50
