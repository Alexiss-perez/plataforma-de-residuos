from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def create(self, **fields: Any) -> User:
        user = User(**fields)
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def update(self, user: User, fields: dict[str, Any]) -> User:
        for key, value in fields.items():
            setattr(user, key, value)
        self.db.flush()
        self.db.refresh(user)
        return user

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        return self.db.scalars(select(User).offset(skip).limit(limit)).all()
