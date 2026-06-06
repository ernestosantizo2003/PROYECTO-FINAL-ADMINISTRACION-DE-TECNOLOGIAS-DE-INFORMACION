from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status

from core.config import settings
from core.logging_config import get_logger
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.repositories.role_repository import RoleRepository
from infrastructure.security.jwt_handler import create_access_token
from infrastructure.security.password_handler import verify_password

logger = get_logger(__name__)


class LoginUseCase:

    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def execute(self, username: str, password: str) -> dict:
        """Authenticate user and return JWT token with user info."""
        # Try login with username first, then email
        user: Optional[User] = self.user_repo.get_by_username(username)
        if not user:
            user = self.user_repo.get_by_email(username)

        if not user:
            logger.warning(f"Login attempt for non-existent user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta desactivada",
            )

        if not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Load role details
        role = self.role_repo.get_by_id(user.role_id)
        role_name = role.name if role else "unknown"

        # Create token
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": role_name,
        }
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        logger.info(f"User '{user.username}' logged in successfully with role '{role_name}'")

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": role_name,
                "role_id": str(user.role_id),
            },
        }
