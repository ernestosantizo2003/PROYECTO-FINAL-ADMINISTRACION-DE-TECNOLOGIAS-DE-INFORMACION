from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str
    username: str
    hashed_password: str
    full_name: str
    is_active: bool
    role_id: UUID
    created_at: datetime
    updated_at: datetime
    role_name: Optional[str] = None
