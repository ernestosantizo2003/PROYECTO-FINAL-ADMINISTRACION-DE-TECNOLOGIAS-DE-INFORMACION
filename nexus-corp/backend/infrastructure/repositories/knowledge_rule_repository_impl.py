from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.knowledge_rule import KnowledgeRule
from domain.repositories.knowledge_rule_repository import KnowledgeRuleRepository
from infrastructure.database.models import KnowledgeRuleModel


def _model_to_entity(model: KnowledgeRuleModel) -> KnowledgeRule:
    return KnowledgeRule(
        id=model.id,
        name=model.name,
        description=model.description,
        conditions=model.conditions,
        action=model.action,
        priority=model.priority,
        category=model.category,
        is_active=model.is_active,
        created_by=model.created_by,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class KnowledgeRuleRepositoryImpl(KnowledgeRuleRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, rule_id: UUID) -> Optional[KnowledgeRule]:
        model = self.db.query(KnowledgeRuleModel).filter(KnowledgeRuleModel.id == rule_id).first()
        return _model_to_entity(model) if model else None

    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> List[KnowledgeRule]:
        query = self.db.query(KnowledgeRuleModel)
        if is_active is not None:
            query = query.filter(KnowledgeRuleModel.is_active == is_active)
        if category:
            query = query.filter(KnowledgeRuleModel.category == category)
        query = query.order_by(KnowledgeRuleModel.priority.asc(), KnowledgeRuleModel.created_at.desc())
        models = query.offset(skip).limit(limit).all()
        return [_model_to_entity(m) for m in models]

    def list_active(self) -> List[KnowledgeRule]:
        models = (
            self.db.query(KnowledgeRuleModel)
            .filter(KnowledgeRuleModel.is_active == True)  # noqa: E712
            .order_by(KnowledgeRuleModel.priority.asc())
            .all()
        )
        return [_model_to_entity(m) for m in models]

    def create(self, rule: KnowledgeRule) -> KnowledgeRule:
        model = KnowledgeRuleModel(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            conditions=rule.conditions,
            action=rule.action,
            priority=rule.priority,
            category=rule.category,
            is_active=rule.is_active,
            created_by=rule.created_by,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def update(self, rule: KnowledgeRule) -> KnowledgeRule:
        model = self.db.query(KnowledgeRuleModel).filter(KnowledgeRuleModel.id == rule.id).first()
        if not model:
            raise ValueError(f"KnowledgeRule {rule.id} not found")
        model.name = rule.name
        model.description = rule.description
        model.conditions = rule.conditions
        model.action = rule.action
        model.priority = rule.priority
        model.category = rule.category
        model.is_active = rule.is_active
        model.updated_at = rule.updated_at
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def delete(self, rule_id: UUID) -> bool:
        model = self.db.query(KnowledgeRuleModel).filter(KnowledgeRuleModel.id == rule_id).first()
        if not model:
            return False
        model.is_active = False  # Soft delete
        self.db.commit()
        return True

    def count(self) -> int:
        return self.db.query(KnowledgeRuleModel).filter(KnowledgeRuleModel.is_active == True).count()  # noqa: E712

    def count_by_category(self) -> List[dict]:
        from sqlalchemy import func
        results = (
            self.db.query(KnowledgeRuleModel.category, func.count(KnowledgeRuleModel.id))
            .filter(KnowledgeRuleModel.is_active == True)  # noqa: E712
            .group_by(KnowledgeRuleModel.category)
            .all()
        )
        return [{"category": r[0], "count": r[1]} for r in results]
