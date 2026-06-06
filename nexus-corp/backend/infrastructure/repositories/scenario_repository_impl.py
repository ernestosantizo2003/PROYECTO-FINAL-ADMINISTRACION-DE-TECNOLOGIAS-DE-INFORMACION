from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.scenario import Scenario
from domain.repositories.scenario_repository import ScenarioRepository
from infrastructure.database.models import ScenarioModel


def _model_to_entity(model: ScenarioModel) -> Scenario:
    return Scenario(
        id=model.id,
        name=model.name,
        description=model.description,
        stock_level=model.stock_level,
        demand_level=model.demand_level,
        risk_level=model.risk_level,
        created_by=model.created_by,
        created_at=model.created_at,
    )


class ScenarioRepositoryImpl(ScenarioRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, scenario_id: UUID) -> Optional[Scenario]:
        model = self.db.query(ScenarioModel).filter(ScenarioModel.id == scenario_id).first()
        return _model_to_entity(model) if model else None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Scenario]:
        models = (
            self.db.query(ScenarioModel)
            .order_by(ScenarioModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_model_to_entity(m) for m in models]

    def create(self, scenario: Scenario) -> Scenario:
        model = ScenarioModel(
            id=scenario.id,
            name=scenario.name,
            description=scenario.description,
            stock_level=scenario.stock_level,
            demand_level=scenario.demand_level,
            risk_level=scenario.risk_level,
            created_by=scenario.created_by,
            created_at=scenario.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def delete(self, scenario_id: UUID) -> bool:
        model = self.db.query(ScenarioModel).filter(ScenarioModel.id == scenario_id).first()
        if not model:
            return False
        self.db.delete(model)
        self.db.commit()
        return True

    def count(self) -> int:
        return self.db.query(ScenarioModel).count()
