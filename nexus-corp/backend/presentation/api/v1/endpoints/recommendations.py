from uuid import UUID

from fastapi import APIRouter, Depends

from presentation.dependencies import get_recommendation_repo, get_current_user, CurrentUser
from presentation.schemas.recommendation_schemas import (
    RecommendationListResponse,
    RecommendationResponse,
)

router = APIRouter(prefix="/recommendations", tags=["Recomendaciones"])


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


@router.get(
    "/decision/{decision_id}",
    response_model=RecommendationListResponse,
    summary="Recomendaciones por decisión",
)
def get_recommendations_by_decision(
    decision_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    recommendation_repo=Depends(get_recommendation_repo),
):
    """Get all recommendations for a specific decision."""
    recs = recommendation_repo.get_by_decision_id(decision_id)
    return RecommendationListResponse(recommendations=[_rec_to_response(r) for r in recs])
