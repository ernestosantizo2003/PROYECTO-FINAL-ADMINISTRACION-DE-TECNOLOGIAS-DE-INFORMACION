from fastapi import APIRouter

from presentation.api.v1.endpoints import (
    auth,
    users,
    roles,
    knowledge_rules,
    scenarios,
    decisions,
    recommendations,
    feedback,
    kpis,
    audit,
)

api_router = APIRouter(prefix="/api/v1")

# Register all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(knowledge_rules.router)
api_router.include_router(scenarios.router)
api_router.include_router(decisions.router)
api_router.include_router(recommendations.router)
api_router.include_router(feedback.router)
api_router.include_router(kpis.router)
api_router.include_router(audit.router)
