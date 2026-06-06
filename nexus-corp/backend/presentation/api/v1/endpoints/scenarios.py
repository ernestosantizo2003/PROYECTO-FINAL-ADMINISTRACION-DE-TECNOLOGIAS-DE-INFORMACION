from uuid import UUID

from fastapi import APIRouter, Depends, Query

from application.use_cases.scenario_use_cases import (
    CreateScenarioUseCase,
    DeleteScenarioUseCase,
    GetScenarioUseCase,
    ListScenariosUseCase,
)
from presentation.dependencies import get_scenario_repo, require_role, CurrentUser
from presentation.schemas.scenario_schemas import (
    ScenarioCreateRequest,
    ScenarioListResponse,
    ScenarioResponse,
)

router = APIRouter(prefix="/scenarios", tags=["Escenarios"])

DECISOR_AND_UP = require_role("decisor", "admin_sistema", "admin_conocimiento")


def _scenario_to_response(scenario) -> ScenarioResponse:
    return ScenarioResponse(
        id=scenario.id,
        name=scenario.name,
        description=scenario.description,
        stock_level=scenario.stock_level,
        demand_level=scenario.demand_level,
        risk_level=scenario.risk_level,
        created_by=scenario.created_by,
        created_at=scenario.created_at,
    )


@router.get("/", response_model=ScenarioListResponse, summary="Listar escenarios")
def list_scenarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(DECISOR_AND_UP),
    scenario_repo=Depends(get_scenario_repo),
):
    use_case = ListScenariosUseCase(scenario_repo=scenario_repo)
    scenarios = use_case.execute(skip=skip, limit=limit)
    total = scenario_repo.count()
    return ScenarioListResponse(
        scenarios=[_scenario_to_response(s) for s in scenarios],
        total=total,
    )


@router.post("/", response_model=ScenarioResponse, status_code=201, summary="Crear escenario")
def create_scenario(
    body: ScenarioCreateRequest,
    current_user: CurrentUser = Depends(DECISOR_AND_UP),
    scenario_repo=Depends(get_scenario_repo),
):
    use_case = CreateScenarioUseCase(scenario_repo=scenario_repo)
    scenario = use_case.execute(
        name=body.name,
        description=body.description,
        stock_level=body.stock_level,
        demand_level=body.demand_level,
        risk_level=body.risk_level,
        created_by=current_user.user_id,
    )
    return _scenario_to_response(scenario)


@router.get("/{scenario_id}", response_model=ScenarioResponse, summary="Obtener escenario")
def get_scenario(
    scenario_id: UUID,
    current_user: CurrentUser = Depends(DECISOR_AND_UP),
    scenario_repo=Depends(get_scenario_repo),
):
    use_case = GetScenarioUseCase(scenario_repo=scenario_repo)
    scenario = use_case.execute(scenario_id=scenario_id)
    return _scenario_to_response(scenario)


@router.delete("/{scenario_id}", summary="Eliminar escenario")
def delete_scenario(
    scenario_id: UUID,
    current_user: CurrentUser = Depends(DECISOR_AND_UP),
    scenario_repo=Depends(get_scenario_repo),
):
    use_case = DeleteScenarioUseCase(scenario_repo=scenario_repo)
    use_case.execute(scenario_id=scenario_id)
    return {"message": f"Escenario {scenario_id} eliminado correctamente"}
