from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from domain.entities.kpi import KPI
from domain.repositories.kpi_repository import KPIRepository
from infrastructure.database.models import KPIModel


def _model_to_entity(model: KPIModel) -> KPI:
    return KPI(
        id=model.id,
        name=model.name,
        value=model.value,
        unit=model.unit,
        period=model.period,
        category=model.category,
        created_at=model.created_at,
    )


class KPIRepositoryImpl(KPIRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, kpi_id: UUID) -> Optional[KPI]:
        model = self.db.query(KPIModel).filter(KPIModel.id == kpi_id).first()
        return _model_to_entity(model) if model else None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[KPI]:
        models = (
            self.db.query(KPIModel)
            .order_by(KPIModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_model_to_entity(m) for m in models]

    def create(self, kpi: KPI) -> KPI:
        model = KPIModel(
            id=kpi.id,
            name=kpi.name,
            value=kpi.value,
            unit=kpi.unit,
            period=kpi.period,
            category=kpi.category,
            created_at=kpi.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def get_by_category(self, category: str) -> List[KPI]:
        models = (
            self.db.query(KPIModel)
            .filter(KPIModel.category == category)
            .order_by(KPIModel.created_at.desc())
            .all()
        )
        return [_model_to_entity(m) for m in models]

    def count_by_category(self) -> List[dict]:
        results = (
            self.db.query(KPIModel.category, func.count(KPIModel.id))
            .group_by(KPIModel.category)
            .all()
        )
        return [{"category": r[0], "count": r[1]} for r in results]
