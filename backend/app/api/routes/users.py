from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import UserPublic, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
def get_me(user: User = Depends(get_current_user)):
    return UserService.to_public(user)


@router.patch("/me", response_model=UserPublic)
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updated = UserService(db).update_profile(user, data)
    db.commit()
    return UserService.to_public(updated)
