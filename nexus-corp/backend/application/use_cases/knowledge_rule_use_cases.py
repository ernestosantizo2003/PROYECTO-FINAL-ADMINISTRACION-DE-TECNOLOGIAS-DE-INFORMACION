import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status

from core.logging_config import get_logger
from domain.entities.knowledge_rule import KnowledgeRule
from domain.entities.audit_log import AuditLog
from domain.repositories.knowledge_rule_repository import KnowledgeRuleRepository
from domain.repositories.audit_repository import AuditRepository

logger = get_logger(__name__)


class ListRulesUseCase:

    def __init__(self, rule_repo: KnowledgeRuleRepository):
        self.rule_repo = rule_repo

    def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> List[KnowledgeRule]:
        return self.rule_repo.list_all(skip=skip, limit=limit, is_active=is_active, category=category)


class GetRuleUseCase:

    def __init__(self, rule_repo: KnowledgeRuleRepository):
        self.rule_repo = rule_repo

    def execute(self, rule_id: uuid.UUID) -> KnowledgeRule:
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Regla {rule_id} no encontrada",
            )
        return rule


class CreateRuleUseCase:

    def __init__(self, rule_repo: KnowledgeRuleRepository, audit_repo: AuditRepository):
        self.rule_repo = rule_repo
        self.audit_repo = audit_repo

    def execute(
        self,
        name: str,
        description: str,
        conditions: Dict[str, Any],
        action: str,
        priority: int,
        category: str,
        created_by: uuid.UUID,
        ip_address: Optional[str] = None,
    ) -> KnowledgeRule:
        now = datetime.utcnow()
        rule = KnowledgeRule(
            id=uuid.uuid4(),
            name=name,
            description=description,
            conditions=conditions,
            action=action,
            priority=priority,
            category=category,
            is_active=True,
            created_by=created_by,
            created_at=now,
            updated_at=now,
        )
        created_rule = self.rule_repo.create(rule)

        self.audit_repo.create(AuditLog(
            id=uuid.uuid4(),
            user_id=created_by,
            action="CREATE",
            entity_type="KnowledgeRule",
            entity_id=created_rule.id,
            details={"name": name, "category": category, "priority": priority},
            ip_address=ip_address,
            created_at=now,
        ))

        logger.info(f"KnowledgeRule '{name}' created by user {created_by}")
        return created_rule


class UpdateRuleUseCase:

    def __init__(self, rule_repo: KnowledgeRuleRepository, audit_repo: AuditRepository):
        self.rule_repo = rule_repo
        self.audit_repo = audit_repo

    def execute(
        self,
        rule_id: uuid.UUID,
        name: Optional[str],
        description: Optional[str],
        conditions: Optional[Dict[str, Any]],
        action: Optional[str],
        priority: Optional[int],
        category: Optional[str],
        is_active: Optional[bool],
        updated_by: uuid.UUID,
        ip_address: Optional[str] = None,
    ) -> KnowledgeRule:
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Regla {rule_id} no encontrada",
            )

        if name is not None:
            rule.name = name
        if description is not None:
            rule.description = description
        if conditions is not None:
            rule.conditions = conditions
        if action is not None:
            rule.action = action
        if priority is not None:
            rule.priority = priority
        if category is not None:
            rule.category = category
        if is_active is not None:
            rule.is_active = is_active

        rule.updated_at = datetime.utcnow()
        updated_rule = self.rule_repo.update(rule)

        self.audit_repo.create(AuditLog(
            id=uuid.uuid4(),
            user_id=updated_by,
            action="UPDATE",
            entity_type="KnowledgeRule",
            entity_id=rule_id,
            details={"name": rule.name},
            ip_address=ip_address,
            created_at=datetime.utcnow(),
        ))

        logger.info(f"KnowledgeRule {rule_id} updated by {updated_by}")
        return updated_rule


class DeleteRuleUseCase:

    def __init__(self, rule_repo: KnowledgeRuleRepository, audit_repo: AuditRepository):
        self.rule_repo = rule_repo
        self.audit_repo = audit_repo

    def execute(
        self,
        rule_id: uuid.UUID,
        deleted_by: uuid.UUID,
        ip_address: Optional[str] = None,
    ) -> bool:
        rule = self.rule_repo.get_by_id(rule_id)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Regla {rule_id} no encontrada",
            )

        success = self.rule_repo.delete(rule_id)

        if success:
            self.audit_repo.create(AuditLog(
                id=uuid.uuid4(),
                user_id=deleted_by,
                action="DELETE",
                entity_type="KnowledgeRule",
                entity_id=rule_id,
                details={"name": rule.name},
                ip_address=ip_address,
                created_at=datetime.utcnow(),
            ))
            logger.info(f"KnowledgeRule {rule_id} soft-deleted by {deleted_by}")

        return success
