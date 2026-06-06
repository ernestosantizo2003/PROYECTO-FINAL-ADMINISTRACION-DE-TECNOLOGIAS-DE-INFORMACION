from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.audit_log import AuditLog
from domain.repositories.audit_repository import AuditRepository
from infrastructure.database.models import AuditLogModel


def _model_to_entity(model: AuditLogModel) -> AuditLog:
    return AuditLog(
        id=model.id,
        user_id=model.user_id,
        action=model.action,
        entity_type=model.entity_type,
        entity_id=model.entity_id,
        details=model.details or {},
        ip_address=model.ip_address,
        created_at=model.created_at,
    )


class AuditRepositoryImpl(AuditRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, audit_id: UUID) -> Optional[AuditLog]:
        model = self.db.query(AuditLogModel).filter(AuditLogModel.id == audit_id).first()
        return _model_to_entity(model) if model else None

    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[UUID] = None,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
    ) -> List[AuditLog]:
        query = self.db.query(AuditLogModel)
        if user_id:
            query = query.filter(AuditLogModel.user_id == user_id)
        if entity_type:
            query = query.filter(AuditLogModel.entity_type == entity_type)
        if action:
            query = query.filter(AuditLogModel.action == action)
        models = (
            query.order_by(AuditLogModel.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_model_to_entity(m) for m in models]

    def create(self, audit_log: AuditLog) -> AuditLog:
        model = AuditLogModel(
            id=audit_log.id,
            user_id=audit_log.user_id,
            action=audit_log.action,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            details=audit_log.details,
            ip_address=audit_log.ip_address,
            created_at=audit_log.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def count(self) -> int:
        return self.db.query(AuditLogModel).count()
