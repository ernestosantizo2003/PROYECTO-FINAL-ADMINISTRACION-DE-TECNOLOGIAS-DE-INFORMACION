from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from domain.entities.decision import Decision
from domain.repositories.decision_repository import DecisionRepository
from infrastructure.database.models import DecisionModel


def _model_to_entity(model: DecisionModel) -> Decision:
    return Decision(
        id=model.id,
        scenario_id=model.scenario_id,
        recommendations=model.recommendations or [],
        rules_fired=[UUID(str(r)) if isinstance(r, str) else r for r in (model.rules_fired or [])],
        status=model.status,
        notes=model.notes,
        created_by=model.created_by,
        created_at=model.created_at,
    )


class DecisionRepositoryImpl(DecisionRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, decision_id: UUID) -> Optional[Decision]:
        model = self.db.query(DecisionModel).filter(DecisionModel.id == decision_id).first()
        return _model_to_entity(model) if model else None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Decision]:
        models = (
            self.db.query(DecisionModel)
            .order_by(DecisionModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_model_to_entity(m) for m in models]

    def create(self, decision: Decision) -> Decision:
        model = DecisionModel(
            id=decision.id,
            scenario_id=decision.scenario_id,
            recommendations=decision.recommendations,
            rules_fired=[str(r) for r in decision.rules_fired],
            status=decision.status,
            notes=decision.notes,
            created_by=decision.created_by,
            created_at=decision.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def update(self, decision: Decision) -> Decision:
        model = self.db.query(DecisionModel).filter(DecisionModel.id == decision.id).first()
        if not model:
            raise ValueError(f"Decision {decision.id} not found")
        model.status = decision.status
        model.notes = decision.notes
        model.recommendations = decision.recommendations
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def count(self) -> int:
        return self.db.query(DecisionModel).count()

    def count_by_status(self, status: str) -> int:
        return self.db.query(DecisionModel).filter(DecisionModel.status == status).count()

    def count_by_month(self) -> List[dict]:
        results = (
            self.db.query(
                extract("year", DecisionModel.created_at).label("year"),
                extract("month", DecisionModel.created_at).label("month"),
                func.count(DecisionModel.id).label("count"),
            )
            .group_by(
                extract("year", DecisionModel.created_at),
                extract("month", DecisionModel.created_at),
            )
            .order_by(
                extract("year", DecisionModel.created_at).asc(),
                extract("month", DecisionModel.created_at).asc(),
            )
            .limit(12)
            .all()
        )
        return [
            {"year": int(r.year), "month": int(r.month), "count": r.count}
            for r in results
        ]
