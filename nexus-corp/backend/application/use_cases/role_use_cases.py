from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from core.logging_config import get_logger
from domain.entities.role import Role
from domain.repositories.role_repository import RoleRepository

logger = get_logger(__name__)


class ListRolesUseCase:

    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    def execute(self) -> List[Role]:
        return self.role_repo.list_all()


class GetRoleUseCase:

    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    def execute(self, role_id: UUID) -> Role:
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol {role_id} no encontrado",
            )
        return role
