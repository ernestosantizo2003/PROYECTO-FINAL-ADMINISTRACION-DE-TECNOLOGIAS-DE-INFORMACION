from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.scenario import Scenario


class ScenarioRepository(ABC):

    @abstractmethod
    def get_by_id(self, scenario_id: UUID) -> Optional[Scenario]:
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[Scenario]:
        pass

    @abstractmethod
    def create(self, scenario: Scenario) -> Scenario:
        pass

    @abstractmethod
    def delete(self, scenario_id: UUID) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
