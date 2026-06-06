from uuid import UUID

from fastapi import APIRouter, Depends

from application.use_cases.role_use_cases import GetRoleUseCase, ListRolesUseCase
from presentation.dependencies import get_role_repo, require_role, CurrentUser
from presentation.schemas.role_schemas import RoleListResponse, RoleResponse

router = APIRouter(prefix="/roles", tags=["Roles"])

ADMIN_ONLY = require_role("admin_sistema")


def _role_to_response(role) -> RoleResponse:
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=role.permissions,
    )


@router.get("/", response_model=RoleListResponse, summary="Listar roles")
def list_roles(
    current_user: CurrentUser = Depends(ADMIN_ONLY),
    role_repo=Depends(get_role_repo),
):
    use_case = ListRolesUseCase(role_repo=role_repo)
    roles = use_case.execute()
    return RoleListResponse(roles=[_role_to_response(r) for r in roles])


@router.get("/{role_id}", response_model=RoleResponse, summary="Obtener rol")
def get_role(
    role_id: UUID,
    current_user: CurrentUser = Depends(ADMIN_ONLY),
    role_repo=Depends(get_role_repo),
):
    use_case = GetRoleUseCase(role_repo=role_repo)
    role = use_case.execute(role_id=role_id)
    return _role_to_response(role)
