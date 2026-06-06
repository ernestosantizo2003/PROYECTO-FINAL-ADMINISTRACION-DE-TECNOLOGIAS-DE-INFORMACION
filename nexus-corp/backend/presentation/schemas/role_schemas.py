from typing import List
from uuid import UUID

from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str
    permissions: List[str]

    model_config = {"from_attributes": True}


class RoleListResponse(BaseModel):
    roles: List[RoleResponse]
