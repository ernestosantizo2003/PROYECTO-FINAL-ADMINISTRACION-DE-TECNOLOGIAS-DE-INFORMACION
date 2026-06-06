import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status

from core.logging_config import get_logger
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.repositories.role_repository import RoleRepository
from domain.repositories.audit_repository import AuditRepository
from domain.entities.audit_log import AuditLog
from infrastructure.security.password_handler import hash_password

logger = get_logger(__name__)


class CreateUserUseCase:

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        audit_repo: AuditRepository,
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.audit_repo = audit_repo

    def execute(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str,
        role_id: uuid.UUID,
        created_by_id: uuid.UUID,
        ip_address: Optional[str] = None,
    ) -> User:
        # Check duplicate email
        if self.user_repo.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El email '{email}' ya está registrado",
            )
        # Check duplicate username
        if self.user_repo.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El username '{username}' ya está en uso",
            )
        # Validate role
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol {role_id} no encontrado",
            )

        now = datetime.utcnow()
        user = User(
            id=uuid.uuid4(),
            email=email,
            username=username,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_active=True,
            role_id=role_id,
            created_at=now,
            updated_at=now,
        )
        created_user = self.user_repo.create(user)

        # Audit
        self.audit_repo.create(AuditLog(
            id=uuid.uuid4(),
            user_id=created_by_id,
            action="CREATE",
            entity_type="User",
            entity_id=created_user.id,
            details={"username": username, "email": email, "role_id": str(role_id)},
            ip_address=ip_address,
            created_at=now,
        ))

        logger.info(f"User '{username}' created by user {created_by_id}")
        return created_user


class UpdateUserUseCase:

    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        audit_repo: AuditRepository,
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.audit_repo = audit_repo

    def execute(
        self,
        user_id: uuid.UUID,
        full_name: Optional[str],
        email: Optional[str],
        role_id: Optional[uuid.UUID],
        is_active: Optional[bool],
        password: Optional[str],
        updated_by_id: uuid.UUID,
        ip_address: Optional[str] = None,
    ) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado",
            )

        if full_name is not None:
            user.full_name = full_name
        if email is not None and email != user.email:
            if self.user_repo.get_by_email(email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{email}' ya está en uso",
                )
            user.email = email
        if role_id is not None:
            role = self.role_repo.get_by_id(role_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Rol {role_id} no encontrado",
                )
            user.role_id = role_id
        if is_active is not None:
            user.is_active = is_active
        if password:
            user.hashed_password = hash_password(password)

        user.updated_at = datetime.utcnow()
        updated_user = self.user_repo.update(user)

        # Audit
        self.audit_repo.create(AuditLog(
            id=uuid.uuid4(),
            user_id=updated_by_id,
            action="UPDATE",
            entity_type="User",
            entity_id=user_id,
            details={"changes": "user updated"},
            ip_address=ip_address,
            created_at=datetime.utcnow(),
        ))

        logger.info(f"User {user_id} updated by {updated_by_id}")
        return updated_user


class DeleteUserUseCase:

    def __init__(self, user_repo: UserRepository, audit_repo: AuditRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    def execute(
        self,
        user_id: uuid.UUID,
        deleted_by_id: uuid.UUID,
        ip_address: Optional[str] = None,
    ) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado",
            )

        success = self.user_repo.delete(user_id)

        if success:
            self.audit_repo.create(AuditLog(
                id=uuid.uuid4(),
                user_id=deleted_by_id,
                action="DELETE",
                entity_type="User",
                entity_id=user_id,
                details={"username": user.username},
                ip_address=ip_address,
                created_at=datetime.utcnow(),
            ))
            logger.info(f"User {user_id} deactivated by {deleted_by_id}")

        return success


class ListUsersUseCase:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.user_repo.list_all(skip=skip, limit=limit)


class GetUserUseCase:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: uuid.UUID) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario {user_id} no encontrado",
            )
        return user
