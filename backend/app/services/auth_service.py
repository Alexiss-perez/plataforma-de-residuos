from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import RoleEnum
from app.models.models import User
from app.repositories.user_repo import UserRepository
from app.schemas.schemas import TokenResponse, UserLogin, UserPublic, UserRegister


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def register(self, data: UserRegister) -> tuple[User, str]:
        existing = self.repo.get_by_email(data.email)
        if existing:
            raise ConflictError("Email already registered")
        user = self.repo.create(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
            can_collect=data.can_collect,
            commune=data.commune,
            latitude=data.latitude,
            longitude=data.longitude,
        )
        token = create_access_token(user.id, {"role": user.role.value})
        return user, token

    def login(self, data: UserLogin) -> tuple[User, str]:
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise BadRequestError("User is inactive")
        token = create_access_token(user.id, {"role": user.role.value})
        return user, token

    def get_current_user(self, user_id: int) -> User:
        user = self.repo.get(user_id)
        if not user:
            raise UnauthorizedError("User not found")
        return user

    @staticmethod
    def to_public(user: User) -> UserPublic:
        return UserPublic.model_validate(user)

    @staticmethod
    def to_token_response(user: User, token: str) -> TokenResponse:
        return TokenResponse(access_token=token, user=AuthService.to_public(user))
