from fastapi import APIRouter, Depends, Query

from application.use_cases.kpi_use_cases import GetDashboardUseCase, ListKPIsUseCase
from presentation.dependencies import (
    get_current_user,
    get_decision_repo,
    get_feedback_repo,
    get_kpi_repo,
    get_recommendation_repo,
    get_rule_repo,
    get_scenario_repo,
    CurrentUser,
)
from presentation.schemas.kpi_schemas import DashboardResponse, KPIListResponse, KPIResponse

router = APIRouter(prefix="/kpis", tags=["KPIs y Dashboard"])


def _kpi_to_response(kpi) -> KPIResponse:
    return KPIResponse(
        id=kpi.id,
        name=kpi.name,
        value=kpi.value,
        unit=kpi.unit,
        period=kpi.period,
        category=kpi.category,
        created_at=kpi.created_at,
    )


@router.get("/dashboard", response_model=DashboardResponse, summary="Dashboard de KPIs")
def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    kpi_repo=Depends(get_kpi_repo),
    rule_repo=Depends(get_rule_repo),
    scenario_repo=Depends(get_scenario_repo),
    decision_repo=Depends(get_decision_repo),
    recommendation_repo=Depends(get_recommendation_repo),
    feedback_repo=Depends(get_feedback_repo),
):
    """Returns aggregated dashboard metrics for the KBDSS system."""
    use_case = GetDashboardUseCase(
        kpi_repo=kpi_repo,
        rule_repo=rule_repo,
        scenario_repo=scenario_repo,
        decision_repo=decision_repo,
        recommendation_repo=recommendation_repo,
        feedback_repo=feedback_repo,
    )
    data = use_case.execute()
    return DashboardResponse(**data)


@router.get("/", response_model=KPIListResponse, summary="Listar KPIs")
def list_kpis(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    kpi_repo=Depends(get_kpi_repo),
):
    use_case = ListKPIsUseCase(kpi_repo=kpi_repo)
    kpis = use_case.execute(skip=skip, limit=limit)
    total = kpi_repo.count_by_category()  # reuse to get total count
    # total is list of {category, count}, sum them up
    total_count = sum(item["count"] for item in total)
    return KPIListResponse(
        kpis=[_kpi_to_response(k) for k in kpis],
        total=total_count,
    )
