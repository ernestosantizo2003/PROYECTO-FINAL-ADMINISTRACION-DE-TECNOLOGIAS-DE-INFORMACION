from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


VALID_PRIORITIES = {1, 2, 3}


class KnowledgeRuleCreateRequest(BaseModel):
    name: str
    description: str = ""
    conditions: Dict[str, Any]
    action: str
    priority: int = 2  # 1=alta, 2=media, 3=baja
    category: str = "general"

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: int) -> int:
        if v not in VALID_PRIORITIES:
            raise ValueError("priority debe ser 1 (alta), 2 (media) o 3 (baja)")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Stock Critico Alta Demanda",
                "description": "Regla para stock crítico con demanda alta",
                "conditions": {
                    "stock_level": {"operator": "<", "value": 20},
                    "demand_level": {"operator": "==", "value": "alto"},
                },
                "action": "Generar orden de compra urgente",
                "priority": 1,
                "category": "inventario",
            }
        }
    }


class KnowledgeRuleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v not in VALID_PRIORITIES:
            raise ValueError("priority debe ser 1 (alta), 2 (media) o 3 (baja)")
        return v


class KnowledgeRuleResponse(BaseModel):
    id: UUID
    name: str
    description: str
    conditions: Dict[str, Any]
    action: str
    priority: int
    category: str
    is_active: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeRuleListResponse(BaseModel):
    rules: List[KnowledgeRuleResponse]
    total: int
