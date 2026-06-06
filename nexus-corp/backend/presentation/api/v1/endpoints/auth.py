from fastapi import APIRouter, Depends, Request

from application.use_cases.auth_use_cases import LoginUseCase
from presentation.dependencies import (
    get_current_user,
    get_role_repo,
    get_user_repo,
    CurrentUser,
)
from presentation.schemas.auth_schemas import LoginRequest, LoginResponse, UserInfoResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse, summary="Iniciar sesión")
def login(
    body: LoginRequest,
    user_repo=Depends(get_user_repo),
    role_repo=Depends(get_role_repo),
):
    """Authenticate user with username/email and password. Returns JWT token."""
    use_case = LoginUseCase(user_repo=user_repo, role_repo=role_repo)
    result = use_case.execute(username=body.username, password=body.password)
    return result


@router.post("/logout", summary="Cerrar sesión")
def logout(current_user: CurrentUser = Depends(get_current_user)):
    """Logout endpoint. Client should discard the JWT token."""
    return {"message": f"Sesión cerrada para '{current_user.username}'"}


@router.get("/me", response_model=UserInfoResponse, summary="Usuario actual")
def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    user_repo=Depends(get_user_repo),
    role_repo=Depends(get_role_repo),
):
    """Return information about the currently authenticated user."""
    user = user_repo.get_by_id(current_user.user_id)
    role = role_repo.get_by_id(user.role_id)
    return UserInfoResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=role.name if role else current_user.role,
        role_id=str(user.role_id),
    )
