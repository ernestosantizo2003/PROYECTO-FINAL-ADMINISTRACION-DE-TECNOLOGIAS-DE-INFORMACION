from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.decision import Decision


class DecisionRepository(ABC):

    @abstractmethod
    def get_by_id(self, decision_id: UUID) -> Optional[Decision]:
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[Decision]:
        pass

    @abstractmethod
    def create(self, decision: Decision) -> Decision:
        pass

    @abstractmethod
    def update(self, decision: Decision) -> Decision:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def count_by_status(self, status: str) -> int:
        pass

    @abstractmethod
    def count_by_month(self) -> List[dict]:
        pass
