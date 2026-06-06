from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from infrastructure.database.models import UserModel


def _model_to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        username=model.username,
        hashed_password=model.hashed_password,
        full_name=model.full_name,
        is_active=model.is_active,
        role_id=model.role_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
        role_name=model.role.name if model.role else None,
    )


class UserRepositoryImpl(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return _model_to_entity(model) if model else None

    def get_by_email(self, email: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return _model_to_entity(model) if model else None

    def get_by_username(self, username: str) -> Optional[User]:
        model = self.db.query(UserModel).filter(UserModel.username == username).first()
        return _model_to_entity(model) if model else None

    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        models = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [_model_to_entity(m) for m in models]

    def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            role_id=user.role_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def update(self, user: User) -> User:
        model = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if not model:
            raise ValueError(f"User {user.id} not found")
        model.email = user.email
        model.username = user.username
        model.full_name = user.full_name
        model.is_active = user.is_active
        model.role_id = user.role_id
        model.hashed_password = user.hashed_password
        model.updated_at = user.updated_at
        self.db.commit()
        self.db.refresh(model)
        return _model_to_entity(model)

    def delete(self, user_id: UUID) -> bool:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not model:
            return False
        model.is_active = False
        self.db.commit()
        return True

    def count(self) -> int:
        return self.db.query(UserModel).count()
