from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.kpi import KPI


class KPIRepository(ABC):

    @abstractmethod
    def get_by_id(self, kpi_id: UUID) -> Optional[KPI]:
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[KPI]:
        pass

    @abstractmethod
    def create(self, kpi: KPI) -> KPI:
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[KPI]:
        pass

    @abstractmethod
    def count_by_category(self) -> List[dict]:
        pass
