from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from domain.entities.feedback import Feedback
from domain.repositories.feedback_repository import FeedbackRepository
from infrastructure.database.models import FeedbackModel


def _model_to_entity(model: FeedbackModel) -> Feedback:
    return Feedback(
        id=model.id,
        decision_id=model.decision_id,
        user_id=model.user_id,
        rating=model.rating,
        comment=model.comment,
        created_at=model.created_at,
    )


class FeedbackRepositoryImpl(FeedbackRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, feedback_id: UUID) -> Optional[Feedback]:
        model = self.db.query(FeedbackModel).filter(FeedbackModel.id == feedback_id).first()
        return _model_to_entity(model) if model else None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Feedback]:
        models = (
            self.db.query(FeedbackModel)
            .order_by(FeedbackModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_model_to_entity(m) for m in models]

    def create(self, feedback: Feedback) -> Feedback:
        model = FeedbackModel(
            id=feedback.id,
            decision_id=feedback.decision_id,
            user_id=feedback.user_id,
            rating=feedback.rating,
            comment=feedback.comment,
            created_at=feedback.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def get_average_rating(self) -> float:
        result = self.db.query(func.avg(FeedbackModel.rating)).scalar()
        return round(float(result), 2) if result else 0.0

    def count(self) -> int:
        return self.db.query(FeedbackModel).count()

    def get_rating_distribution(self) -> List[dict]:
        results = (
            self.db.query(FeedbackModel.rating, func.count(FeedbackModel.id))
            .group_by(FeedbackModel.rating)
            .order_by(FeedbackModel.rating.asc())
            .all()
        )
        return [{"rating": r[0], "count": r[1]} for r in results]
