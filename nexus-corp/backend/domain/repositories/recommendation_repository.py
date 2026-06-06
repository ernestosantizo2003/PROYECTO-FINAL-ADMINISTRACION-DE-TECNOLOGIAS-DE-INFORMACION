from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.recommendation import Recommendation


class RecommendationRepository(ABC):

    @abstractmethod
    def get_by_id(self, rec_id: UUID) -> Optional[Recommendation]:
        pass

    @abstractmethod
    def get_by_decision_id(self, decision_id: UUID) -> List[Recommendation]:
        pass

    @abstractmethod
    def create(self, recommendation: Recommendation) -> Recommendation:
        pass

    @abstractmethod
    def create_many(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        pass

    @abstractmethod
    def update(self, recommendation: Recommendation) -> Recommendation:
        pass

    @abstractmethod
    def count_accepted(self) -> int:
        pass

    @abstractmethod
    def count_rejected(self) -> int:
        pass
