from fastapi import APIRouter, Depends, Query

from application.use_cases.feedback_use_cases import (
    CreateFeedbackUseCase,
    GetFeedbackStatsUseCase,
    ListFeedbackUseCase,
)
from presentation.dependencies import (
    get_current_user,
    get_decision_repo,
    get_feedback_repo,
    CurrentUser,
)
from presentation.schemas.feedback_schemas import (
    FeedbackCreateRequest,
    FeedbackListResponse,
    FeedbackResponse,
    FeedbackStatsResponse,
)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


def _feedback_to_response(fb) -> FeedbackResponse:
    return FeedbackResponse(
        id=fb.id,
        decision_id=fb.decision_id,
        user_id=fb.user_id,
        rating=fb.rating,
        comment=fb.comment,
        created_at=fb.created_at,
    )


@router.get("/stats", response_model=FeedbackStatsResponse, summary="Estadísticas de feedback")
def get_feedback_stats(
    current_user: CurrentUser = Depends(get_current_user),
    feedback_repo=Depends(get_feedback_repo),
):
    use_case = GetFeedbackStatsUseCase(feedback_repo=feedback_repo)
    stats = use_case.execute()
    return FeedbackStatsResponse(
        average_rating=stats["average_rating"],
        total_count=stats["total_count"],
        distribution=stats["distribution"],
    )


@router.get("/", response_model=FeedbackListResponse, summary="Listar feedback")
def list_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(get_current_user),
    feedback_repo=Depends(get_feedback_repo),
):
    use_case = ListFeedbackUseCase(feedback_repo=feedback_repo)
    feedbacks = use_case.execute(skip=skip, limit=limit)
    total = feedback_repo.count()
    return FeedbackListResponse(
        items=[_feedback_to_response(f) for f in feedbacks],
        total=total,
    )


@router.post(
    "/",
    response_model=FeedbackResponse,
    status_code=201,
    summary="Crear feedback",
)
def create_feedback(
    body: FeedbackCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    feedback_repo=Depends(get_feedback_repo),
    decision_repo=Depends(get_decision_repo),
):
    use_case = CreateFeedbackUseCase(
        feedback_repo=feedback_repo,
        decision_repo=decision_repo,
    )
    feedback = use_case.execute(
        decision_id=body.decision_id,
        user_id=current_user.user_id,
        rating=body.rating,
        comment=body.comment,
    )
    return _feedback_to_response(feedback)
