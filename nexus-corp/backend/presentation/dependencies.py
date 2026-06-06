from typing import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.logging_config import get_logger
from infrastructure.database.connection import get_db
from infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from infrastructure.repositories.role_repository_impl import RoleRepositoryImpl
from infrastructure.repositories.knowledge_rule_repository_impl import KnowledgeRuleRepositoryImpl
from infrastructure.repositories.scenario_repository_impl import ScenarioRepositoryImpl
from infrastructure.repositories.decision_repository_impl import DecisionRepositoryImpl
from infrastructure.repositories.recommendation_repository_impl import RecommendationRepositoryImpl
from infrastructure.repositories.feedback_repository_impl import FeedbackRepositoryImpl
from infrastructure.repositories.kpi_repository_impl import KPIRepositoryImpl
from infrastructure.repositories.audit_repository_impl import AuditRepositoryImpl
from infrastructure.security.jwt_handler import decode_access_token

logger = get_logger(__name__)

bearer_scheme = HTTPBearer()


# ─── Repository Dependencies ────────────────────────────────────────────────

def get_user_repo(db: Session = Depends(get_db)) -> UserRepositoryImpl:
    return UserRepositoryImpl(db)


def get_role_repo(db: Session = Depends(get_db)) -> RoleRepositoryImpl:
    return RoleRepositoryImpl(db)


def get_rule_repo(db: Session = Depends(get_db)) -> KnowledgeRuleRepositoryImpl:
    return KnowledgeRuleRepositoryImpl(db)


def get_scenario_repo(db: Session = Depends(get_db)) -> ScenarioRepositoryImpl:
    return ScenarioRepositoryImpl(db)


def get_decision_repo(db: Session = Depends(get_db)) -> DecisionRepositoryImpl:
    return DecisionRepositoryImpl(db)


def get_recommendation_repo(db: Session = Depends(get_db)) -> RecommendationRepositoryImpl:
    return RecommendationRepositoryImpl(db)


def get_feedback_repo(db: Session = Depends(get_db)) -> FeedbackRepositoryImpl:
    return FeedbackRepositoryImpl(db)


def get_kpi_repo(db: Session = Depends(get_db)) -> KPIRepositoryImpl:
    return KPIRepositoryImpl(db)


def get_audit_repo(db: Session = Depends(get_db)) -> AuditRepositoryImpl:
    return AuditRepositoryImpl(db)


# ─── Auth Dependencies ───────────────────────────────────────────────────────

class CurrentUser:
    """Simple container for the authenticated user info extracted from JWT."""

    def __init__(self, user_id: UUID, username: str, role: str):
        self.user_id = user_id
        self.username = username
        self.role = role


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: UserRepositoryImpl = Depends(get_user_repo),
) -> CurrentUser:
    """Validate JWT and return the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    # Verify user still exists and is active
    user = user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )

    return CurrentUser(
        user_id=user.id,
        username=user.username,
        role=user.role_name or payload.get("role", ""),
    )


def require_role(*allowed_roles: str) -> Callable:
    """Factory that returns a FastAPI dependency enforcing role-based access."""

    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker
