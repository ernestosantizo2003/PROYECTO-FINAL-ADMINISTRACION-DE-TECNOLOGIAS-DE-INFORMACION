from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.user import User


class UserRepository(ABC):

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: UUID) -> bool:
        pass

    @abstractmethod
    def count(self) -> int:
        pass
