from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.feedback import Feedback


class FeedbackRepository(ABC):

    @abstractmethod
    def get_by_id(self, feedback_id: UUID) -> Optional[Feedback]:
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[Feedback]:
        pass

    @abstractmethod
    def create(self, feedback: Feedback) -> Feedback:
        pass

    @abstractmethod
    def get_average_rating(self) -> float:
        pass

    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def get_rating_distribution(self) -> List[dict]:
        pass
