from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import NotificationPublic
from app.repositories.repos import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationPublic])
def list_mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [NotificationPublic.model_validate(n) for n in NotificationRepository(db).list_by_user(user.id)]


@router.post("/{notification_id}/read", response_model=NotificationPublic)
def mark_read(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    repo = NotificationRepository(db)
    n = repo.get(notification_id)
    if not n or n.user_id != user.id:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Notification not found")
    n.read = True
    db.flush()
    db.commit()
    db.refresh(n)
    return NotificationPublic.model_validate(n)
