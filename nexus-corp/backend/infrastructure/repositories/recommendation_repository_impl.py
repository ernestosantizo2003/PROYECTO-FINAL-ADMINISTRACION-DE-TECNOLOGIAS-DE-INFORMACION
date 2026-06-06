from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.recommendation import Recommendation
from domain.repositories.recommendation_repository import RecommendationRepository
from infrastructure.database.models import RecommendationModel


def _model_to_entity(model: RecommendationModel) -> Recommendation:
    return Recommendation(
        id=model.id,
        decision_id=model.decision_id,
        rule_id=model.rule_id,
        text=model.text,
        priority=model.priority,
        justification=model.justification,
        is_accepted=model.is_accepted,
    )


class RecommendationRepositoryImpl(RecommendationRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, rec_id: UUID) -> Optional[Recommendation]:
        model = self.db.query(RecommendationModel).filter(RecommendationModel.id == rec_id).first()
        return _model_to_entity(model) if model else None

    def get_by_decision_id(self, decision_id: UUID) -> List[Recommendation]:
        models = (
            self.db.query(RecommendationModel)
            .filter(RecommendationModel.decision_id == decision_id)
            .order_by(RecommendationModel.priority.asc())
            .all()
        )
        return [_model_to_entity(m) for m in models]

    def create(self, recommendation: Recommendation) -> Recommendation:
        model = RecommendationModel(
            id=recommendation.id,
            decision_id=recommendation.decision_id,
            rule_id=recommendation.rule_id,
            text=recommendation.text,
            priority=recommendation.priority,
            justification=recommendation.justification,
            is_accepted=recommendation.is_accepted,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def create_many(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        models = [
            RecommendationModel(
                id=r.id,
                decision_id=r.decision_id,
                rule_id=r.rule_id,
                text=r.text,
                priority=r.priority,
                justification=r.justification,
                is_accepted=r.is_accepted,
            )
            for r in recommendations
        ]
        self.db.add_all(models)
        self.db.commit()
        for model in models:
            self.db.refresh(model)
        return [_model_to_entity(m) for m in models]

    def update(self, recommendation: Recommendation) -> Recommendation:
        model = (
            self.db.query(RecommendationModel)
            .filter(RecommendationModel.id == recommendation.id)
            .first()
        )
        if not model:
            raise ValueError(f"Recommendation {recommendation.id} not found")
        model.is_accepted = recommendation.is_accepted
        model.text = recommendation.text
        model.justification = recommendation.justification
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def count_accepted(self) -> int:
        return (
            self.db.query(RecommendationModel)
            .filter(RecommendationModel.is_accepted == True)  # noqa: E712
            .count()
        )

    def count_rejected(self) -> int:
        return (
            self.db.query(RecommendationModel)
            .filter(RecommendationModel.is_accepted == False)  # noqa: E712
            .count()
        )
