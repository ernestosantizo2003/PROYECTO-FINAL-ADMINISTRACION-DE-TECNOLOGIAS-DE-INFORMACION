from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from application.use_cases.decision_use_cases import (
    AnalyzeDecisionUseCase,
    GetDecisionUseCase,
    ListDecisionsUseCase,
    UpdateDecisionStatusUseCase,
)
from application.services.rule_engine import RuleEngine
from presentation.dependencies import (
    get_audit_repo,
    get_decision_repo,
    get_recommendation_repo,
    get_rule_repo,
    get_scenario_repo,
    require_role,
    CurrentUser,
)
from presentation.schemas.decision_schemas import (
    AnalyzeRequest,
    DecisionListResponse,
    DecisionResponse,
    DecisionStatusUpdateRequest,
    DecisionWithRecommendationsResponse,
    RecommendationResponse,
)

router = APIRouter(prefix="/decisions", tags=["Decisiones"])

DECISOR_AND_UP = require_role("decisor", "admin_sistema", "admin_conocimiento")


def _decision_to_response(decision) -> DecisionResponse:
    return DecisionResponse(
        id=decision.id,
        scenario_id=decision.scenario_id,
        recommendations=decision.recommendations,
        rules_fired=[str(r) for r in decision.rules_fired],
        status=decision.status,
        notes=decision.notes,
        created_by=decision.created_by,
        created_at=decision.created_at,
    )


def _rec_to_response(rec) -> RecommendationResponse:
    return RecommendationResponse(
        id=rec.id,
        decision_id=rec.decision_id,
        rule_id=rec.rule_id,
        text=rec.text,
        priority=rec.priority,
        justification=rec.justification,
        is_accepted=rec.is_accepted,
    )


@router.get("/", response_model=DecisionListResponse, summary="Listar decisiones")
def list_decisions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(DECISOR_AND_UP),
    decision_repo=Depends(get_decision_repo),
):
    use_case = ListDecisionsUseCase(decision_repo=decision_repo)
    decisions = use_case.execute(skip=skip, limit=limit)
    total = decision_repo.count()
    return DecisionListResponse(
        decisions=[_decision_to_response(d) for d in decisions],
        total=total,
    )


@router.post(
    "/analyze",
    response_model=DecisionWithRecommendationsResponse,
    status_code=201,
    summary="Ejecutar análisis what-if",
)
def analyze_scenario(
    body: AnalyzeRequest,
    request: Request,
    current_user: CurrentUser = Depends(DECISOR_AND_UP),
    rule_repo=Depends(get_rule_repo),
    decision_repo=Depends(get_decision_repo),
    recommendation_repo=Depends(get_recommendation_repo),
    scenario_repo=Depends(get_scenario_repo),
    audit_repo=Depends(get_audit_repo),
):
    """
    Execute what-if analysis on a scenario:
    1. Loads all active rules
    2. Evaluates conditions against the scenario parameters
    3. Saves Decision + Recommendation records
    """
    rule_engine = RuleEngine(rule_repository=rule_repo)
    use_case = AnalyzeDecisionUseCase(
        rule_engine=rule_engine,
        decision_repo=decision_repo,
        recommendation_repo=recommendation_repo,
        scenario_repo=scenario_repo,
        audit_repo=audit_repo,
    )
    result = use_case.execute(
        scenario_id=body.scenario_id,
        stock_level=body.stock_level,
        demand_level=body.demand_level,
        risk_level=body.risk_level,
        notes=body.notes,
        created_by=current_user.user_id,
        ip_address=request.client.host if request.client else None,
        scenario_name=body.name,
        scenario_description=body.description,
    )
    return DecisionWithRecommendationsResponse(
        decision=_decision_to_response(result["decision"]),
        recommendations=[_rec_to_response(r) for r in result["recommendations"]],
    )


@router.get(
    "/{decision_id}",
    response_model=DecisionWithRecommendationsResponse,
    summary="Obtener decisión con recomendaciones",
)
def get_decision(
    decision_id: UUID,
    current_user: CurrentUser = Depends(DECISOR_AND_UP),
    decision_repo=Depends(get_decision_repo),
    recommendation_repo=Depends(get_recommendation_repo),
):
    use_case = GetDecisionUseCase(
        decision_repo=decision_repo,
        recommendation_repo=recommendation_repo,
    )
    result = use_case.execute(decision_id=decision_id)
    return DecisionWithRecommendationsResponse(
        decision=_decision_to_response(result["decision"]),
        recommendations=[_rec_to_response(r) for r in result["recommendations"]],
    )


@router.put(
    "/{decision_id}/status",
    response_model=DecisionResponse,
    summary="Actualizar estado de decisión",
)
def update_decision_status(
    decision_id: UUID,
    body: DecisionStatusUpdateRequest,
    request: Request,
    current_user: CurrentUser = Depends(DECISOR_AND_UP),
    decision_repo=Depends(get_decision_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UpdateDecisionStatusUseCase(
        decision_repo=decision_repo,
        audit_repo=audit_repo,
    )
    decision = use_case.execute(
        decision_id=decision_id,
        new_status=body.status,
        notes=body.notes,
        updated_by=current_user.user_id,
        ip_address=request.client.host if request.client else None,
    )
    return _decision_to_response(decision)
