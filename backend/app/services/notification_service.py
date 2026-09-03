from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.enums import NotificationTypeEnum
from app.models.models import Notification


def notify(
    db: Session,
    user_id: int,
    type_: NotificationTypeEnum | str,
    title: str,
    message: str,
) -> Notification:
    if isinstance(type_, NotificationTypeEnum):
        type_str = type_.value
    else:
        type_str = type_
    n = Notification(user_id=user_id, type=type_str, title=title, message=message)
    db.add(n)
    db.flush()
    db.refresh(n)
    return n
