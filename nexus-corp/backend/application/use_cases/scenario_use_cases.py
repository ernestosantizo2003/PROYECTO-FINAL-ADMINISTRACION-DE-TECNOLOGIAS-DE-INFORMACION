import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException, status

from core.logging_config import get_logger
from domain.entities.scenario import Scenario
from domain.repositories.scenario_repository import ScenarioRepository

logger = get_logger(__name__)

VALID_DEMAND_LEVELS = {"bajo", "medio", "alto"}
VALID_RISK_LEVELS = {"bajo", "medio", "alto"}


class ListScenariosUseCase:

    def __init__(self, scenario_repo: ScenarioRepository):
        self.scenario_repo = scenario_repo

    def execute(self, skip: int = 0, limit: int = 100) -> List[Scenario]:
        return self.scenario_repo.list_all(skip=skip, limit=limit)


class GetScenarioUseCase:

    def __init__(self, scenario_repo: ScenarioRepository):
        self.scenario_repo = scenario_repo

    def execute(self, scenario_id: uuid.UUID) -> Scenario:
        scenario = self.scenario_repo.get_by_id(scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Escenario {scenario_id} no encontrado",
            )
        return scenario


class CreateScenarioUseCase:

    def __init__(self, scenario_repo: ScenarioRepository):
        self.scenario_repo = scenario_repo

    def execute(
        self,
        name: str,
        description: str,
        stock_level: int,
        demand_level: str,
        risk_level: str,
        created_by: uuid.UUID,
    ) -> Scenario:
        if demand_level not in VALID_DEMAND_LEVELS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"demand_level debe ser uno de: {', '.join(VALID_DEMAND_LEVELS)}",
            )
        if risk_level not in VALID_RISK_LEVELS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"risk_level debe ser uno de: {', '.join(VALID_RISK_LEVELS)}",
            )
        if not (0 <= stock_level <= 100):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="stock_level debe estar entre 0 y 100",
            )

        scenario = Scenario(
            id=uuid.uuid4(),
            name=name,
            description=description,
            stock_level=stock_level,
            demand_level=demand_level,
            risk_level=risk_level,
            created_by=created_by,
            created_at=datetime.utcnow(),
        )
        created = self.scenario_repo.create(scenario)
        logger.info(f"Scenario '{name}' created by user {created_by}")
        return created


class DeleteScenarioUseCase:

    def __init__(self, scenario_repo: ScenarioRepository):
        self.scenario_repo = scenario_repo

    def execute(self, scenario_id: uuid.UUID) -> bool:
        scenario = self.scenario_repo.get_by_id(scenario_id)
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Escenario {scenario_id} no encontrado",
            )
        success = self.scenario_repo.delete(scenario_id)
        logger.info(f"Scenario {scenario_id} deleted")
        return success
