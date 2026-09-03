from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.models import User
from app.repositories.user_repo import UserRepository
from app.schemas.schemas import UserPublic, UserUpdate


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def get(self, user_id: int) -> User:
        user = self.repo.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def update_profile(self, user: User, data: UserUpdate) -> User:
        fields = data.model_dump(exclude_unset=True)
        return self.repo.update(user, fields)

    @staticmethod
    def to_public(user: User) -> UserPublic:
        return UserPublic.model_validate(user)
