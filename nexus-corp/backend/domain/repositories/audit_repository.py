from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.audit_log import AuditLog


class AuditRepository(ABC):

    @abstractmethod
    def get_by_id(self, audit_id: UUID) -> Optional[AuditLog]:
        pass

    @abstractmethod
    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> List[AuditLog]:
        pass

    @abstractmethod
    def create(self, audit_log: AuditLog) -> AuditLog:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
