from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from application.use_cases.user_use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserUseCase,
    ListUsersUseCase,
    UpdateUserUseCase,
)
from presentation.dependencies import (
    get_audit_repo,
    get_role_repo,
    get_user_repo,
    require_role,
    CurrentUser,
)
from presentation.schemas.user_schemas import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/users", tags=["Usuarios"])

ADMIN_ONLY = require_role("admin_sistema")


def _user_to_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        role_id=user.role_id,
        role_name=user.role_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/", response_model=UserListResponse, summary="Listar usuarios")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: CurrentUser = Depends(ADMIN_ONLY),
    user_repo=Depends(get_user_repo),
):
    use_case = ListUsersUseCase(user_repo=user_repo)
    users = use_case.execute(skip=skip, limit=limit)
    total = user_repo.count()
    return UserListResponse(
        items=[_user_to_response(u) for u in users],
        total=total,
    )


@router.post("/", response_model=UserResponse, status_code=201, summary="Crear usuario")
def create_user(
    body: UserCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(ADMIN_ONLY),
    user_repo=Depends(get_user_repo),
    role_repo=Depends(get_role_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = CreateUserUseCase(
        user_repo=user_repo,
        role_repo=role_repo,
        audit_repo=audit_repo,
    )
    user = use_case.execute(
        email=body.email,
        username=body.username,
        password=body.password,
        full_name=body.full_name,
        role_id=body.role_id,
        created_by_id=current_user.user_id,
        ip_address=request.client.host if request.client else None,
    )
    return _user_to_response(user)


@router.get("/{user_id}", response_model=UserResponse, summary="Obtener usuario")
def get_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(ADMIN_ONLY),
    user_repo=Depends(get_user_repo),
):
    use_case = GetUserUseCase(user_repo=user_repo)
    user = use_case.execute(user_id=user_id)
    return _user_to_response(user)


@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar usuario")
def update_user(
    user_id: UUID,
    body: UserUpdateRequest,
    request: Request,
    current_user: CurrentUser = Depends(ADMIN_ONLY),
    user_repo=Depends(get_user_repo),
    role_repo=Depends(get_role_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UpdateUserUseCase(
        user_repo=user_repo,
        role_repo=role_repo,
        audit_repo=audit_repo,
    )
    user = use_case.execute(
        user_id=user_id,
        full_name=body.full_name,
        email=body.email,
        role_id=body.role_id,
        is_active=body.is_active,
        password=body.password,
        updated_by_id=current_user.user_id,
        ip_address=request.client.host if request.client else None,
    )
    return _user_to_response(user)


@router.delete("/{user_id}", summary="Desactivar usuario")
def delete_user(
    user_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(ADMIN_ONLY),
    user_repo=Depends(get_user_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = DeleteUserUseCase(user_repo=user_repo, audit_repo=audit_repo)
    use_case.execute(
        user_id=user_id,
        deleted_by_id=current_user.user_id,
        ip_address=request.client.host if request.client else None,
    )
    return {"message": f"Usuario {user_id} desactivado correctamente"}
