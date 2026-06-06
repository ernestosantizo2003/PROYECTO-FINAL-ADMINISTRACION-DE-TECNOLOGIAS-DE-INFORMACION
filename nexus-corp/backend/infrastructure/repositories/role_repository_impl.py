from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.role import Role
from domain.repositories.role_repository import RoleRepository
from infrastructure.database.models import RoleModel


def _model_to_entity(model: RoleModel) -> Role:
    return Role(
        id=model.id,
        name=model.name,
        description=model.description,
        permissions=model.permissions or [],
    )


class RoleRepositoryImpl(RoleRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, role_id: UUID) -> Optional[Role]:
        model = self.db.query(RoleModel).filter(RoleModel.id == role_id).first()
        return _model_to_entity(model) if model else None

    def get_by_name(self, name: str) -> Optional[Role]:
        model = self.db.query(RoleModel).filter(RoleModel.name == name).first()
        return _model_to_entity(model) if model else None

    def list_all(self) -> List[Role]:
        models = self.db.query(RoleModel).all()
        return [_model_to_entity(m) for m in models]

    def create(self, role: Role) -> Role:
        model = RoleModel(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=role.permissions,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def update(self, role: Role) -> Role:
        model = self.db.query(RoleModel).filter(RoleModel.id == role.id).first()
        if not model:
            raise ValueError(f"Role {role.id} not found")
        model.name = role.name
        model.description = role.description
        model.permissions = role.permissions
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)
