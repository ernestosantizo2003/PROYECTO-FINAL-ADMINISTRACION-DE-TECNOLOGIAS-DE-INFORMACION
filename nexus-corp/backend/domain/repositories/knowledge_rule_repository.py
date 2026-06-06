from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.knowledge_rule import KnowledgeRule


class KnowledgeRuleRepository(ABC):

    @abstractmethod
    def get_by_id(self, rule_id: UUID) -> Optional[KnowledgeRule]:
        pass

    @abstractmethod
    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        category: Optional[str] = None,
    ) -> List[KnowledgeRule]:
        pass

    @abstractmethod
    def list_active(self) -> List[KnowledgeRule]:
        pass

    @abstractmethod
    def create(self, rule: KnowledgeRule) -> KnowledgeRule:
        pass

    @abstractmethod
    def update(self, rule: KnowledgeRule) -> KnowledgeRule:
        pass

    @abstractmethod
    def delete(self, rule_id: UUID) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
