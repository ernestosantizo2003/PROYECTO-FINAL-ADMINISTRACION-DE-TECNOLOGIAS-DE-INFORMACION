from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.role import Role


class RoleRepository(ABC):

    @abstractmethod
    def get_by_id(self, role_id: UUID) -> Optional[Role]:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Role]:
        pass

    @abstractmethod
    def list_all(self) -> List[Role]:
        pass

    @abstractmethod
    def create(self, role: Role) -> Role:
        pass

    @abstractmethod
    def update(self, role: Role) -> Role:
        pass
