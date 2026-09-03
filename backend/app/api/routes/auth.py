from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import TokenResponse, UserLogin, UserPublic, UserRegister, UserUpdate
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    user, token = AuthService(db).register(data)
    db.commit()
    return AuthService.to_token_response(user, token)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user, token = AuthService(db).login(data)
    return AuthService.to_token_response(user, token)


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return UserService.to_public(user)
