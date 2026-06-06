import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException, status

from core.logging_config import get_logger
from domain.entities.feedback import Feedback
from domain.repositories.feedback_repository import FeedbackRepository
from domain.repositories.decision_repository import DecisionRepository

logger = get_logger(__name__)


class ListFeedbackUseCase:

    def __init__(self, feedback_repo: FeedbackRepository):
        self.feedback_repo = feedback_repo

    def execute(self, skip: int = 0, limit: int = 100) -> List[Feedback]:
        return self.feedback_repo.list_all(skip=skip, limit=limit)


class CreateFeedbackUseCase:

    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        decision_repo: DecisionRepository,
    ):
        self.feedback_repo = feedback_repo
        self.decision_repo = decision_repo

    def execute(
        self,
        decision_id: uuid.UUID,
        user_id: uuid.UUID,
        rating: int,
        comment: str,
    ) -> Feedback:
        if not (1 <= rating <= 5):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El rating debe estar entre 1 y 5",
            )

        # Validate decision exists
        decision = self.decision_repo.get_by_id(decision_id)
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision {decision_id} no encontrada",
            )

        feedback = Feedback(
            id=uuid.uuid4(),
            decision_id=decision_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            created_at=datetime.utcnow(),
        )
        created = self.feedback_repo.create(feedback)
        logger.info(f"Feedback created for decision {decision_id} by user {user_id} (rating={rating})")
        return created


class GetFeedbackStatsUseCase:

    def __init__(self, feedback_repo: FeedbackRepository):
        self.feedback_repo = feedback_repo

    def execute(self) -> dict:
        avg_rating = self.feedback_repo.get_average_rating()
        total = self.feedback_repo.count()
        distribution = self.feedback_repo.get_rating_distribution()
        return {
            "average_rating": avg_rating,
            "total_count": total,
            "distribution": distribution,
        }
