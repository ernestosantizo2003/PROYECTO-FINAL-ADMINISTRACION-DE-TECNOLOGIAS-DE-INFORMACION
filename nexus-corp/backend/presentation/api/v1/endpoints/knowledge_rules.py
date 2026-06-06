from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from application.use_cases.knowledge_rule_use_cases import (
    CreateRuleUseCase,
    DeleteRuleUseCase,
    GetRuleUseCase,
    ListRulesUseCase,
    UpdateRuleUseCase,
)
from presentation.dependencies import (
    get_audit_repo,
    get_rule_repo,
    require_role,
    CurrentUser,
)
from presentation.schemas.knowledge_rule_schemas import (
    KnowledgeRuleCreateRequest,
    KnowledgeRuleListResponse,
    KnowledgeRuleResponse,
    KnowledgeRuleUpdateRequest,
)

router = APIRouter(prefix="/rules", tags=["Reglas de Conocimiento"])

KNOWLEDGE_ADMIN = require_role("admin_conocimiento", "admin_sistema")


def _rule_to_response(rule) -> KnowledgeRuleResponse:
    return KnowledgeRuleResponse(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        conditions=rule.conditions,
        action=rule.action,
        priority=rule.priority,
        category=rule.category,
        is_active=rule.is_active,
        created_by=rule.created_by,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
    )


@router.get("/", response_model=KnowledgeRuleListResponse, summary="Listar reglas")
def list_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(KNOWLEDGE_ADMIN),
    rule_repo=Depends(get_rule_repo),
):
    use_case = ListRulesUseCase(rule_repo=rule_repo)
    rules = use_case.execute(skip=skip, limit=limit, is_active=is_active, category=category)
    total = rule_repo.count()
    return KnowledgeRuleListResponse(
        rules=[_rule_to_response(r) for r in rules],
        total=total,
    )


@router.post("/", response_model=KnowledgeRuleResponse, status_code=201, summary="Crear regla")
def create_rule(
    body: KnowledgeRuleCreateRequest,
    request: Request,
    current_user: CurrentUser = Depends(KNOWLEDGE_ADMIN),
    rule_repo=Depends(get_rule_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = CreateRuleUseCase(rule_repo=rule_repo, audit_repo=audit_repo)
    rule = use_case.execute(
        name=body.name,
        description=body.description,
        conditions=body.conditions,
        action=body.action,
        priority=body.priority,
        category=body.category,
        created_by=current_user.user_id,
        ip_address=request.client.host if request.client else None,
    )
    return _rule_to_response(rule)


@router.get("/{rule_id}", response_model=KnowledgeRuleResponse, summary="Obtener regla")
def get_rule(
    rule_id: UUID,
    current_user: CurrentUser = Depends(KNOWLEDGE_ADMIN),
    rule_repo=Depends(get_rule_repo),
):
    use_case = GetRuleUseCase(rule_repo=rule_repo)
    rule = use_case.execute(rule_id=rule_id)
    return _rule_to_response(rule)


@router.put("/{rule_id}", response_model=KnowledgeRuleResponse, summary="Actualizar regla")
def update_rule(
    rule_id: UUID,
    body: KnowledgeRuleUpdateRequest,
    request: Request,
    current_user: CurrentUser = Depends(KNOWLEDGE_ADMIN),
    rule_repo=Depends(get_rule_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = UpdateRuleUseCase(rule_repo=rule_repo, audit_repo=audit_repo)
    rule = use_case.execute(
        rule_id=rule_id,
        name=body.name,
        description=body.description,
        conditions=body.conditions,
        action=body.action,
        priority=body.priority,
        category=body.category,
        is_active=body.is_active,
        updated_by=current_user.user_id,
        ip_address=request.client.host if request.client else None,
    )
    return _rule_to_response(rule)


@router.delete("/{rule_id}", summary="Eliminar regla (soft delete)")
def delete_rule(
    rule_id: UUID,
    request: Request,
    current_user: CurrentUser = Depends(KNOWLEDGE_ADMIN),
    rule_repo=Depends(get_rule_repo),
    audit_repo=Depends(get_audit_repo),
):
    use_case = DeleteRuleUseCase(rule_repo=rule_repo, audit_repo=audit_repo)
    use_case.execute(
        rule_id=rule_id,
        deleted_by=current_user.user_id,
        ip_address=request.client.host if request.client else None,
    )
    return {"message": f"Regla {rule_id} desactivada correctamente"}
