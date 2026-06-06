from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class UserCreateRequest(BaseModel):
    email: str
    username: str
    password: str
    full_name: str
    role_id: UUID

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "nuevo@nexus.com",
                "username": "nuevo_user",
                "password": "SecurePass123",
                "full_name": "Nuevo Usuario",
                "role_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            }
        }
    }


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: str
    is_active: bool
    role_id: UUID
    role_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    skip: int
    limit: int
