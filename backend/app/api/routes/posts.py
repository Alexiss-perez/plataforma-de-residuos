from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.enums import RoleEnum
from app.models.models import Post, User
from app.schemas.schemas import PostCreate, PostPublic, PostUpdate
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])


def _can_see_location(post: Post, user: User) -> bool:
    if user.role == RoleEnum.ADMIN:
        return True
    if post.author_id == user.id:
        return True
    return False


@router.post("", response_model=PostPublic, status_code=201)
def create(data: PostCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = PostService(db).create(user, data)
    db.commit()
    return PostService.to_public(post, include_location=True)


@router.get("", response_model=list[PostPublic])
def list_posts(
    type: str | None = None,
    status: str | None = None,
    commune: str | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    posts = PostService(db).list_filtered(skip, limit, type=type, status=status, commune=commune)
    return [PostService.to_public(p, include_location=_can_see_location(p, user)) for p in posts]


@router.get("/{post_id}", response_model=PostPublic)
def get_post(post_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = PostService(db).get(post_id)
    return PostService.to_public(post, include_location=_can_see_location(post, user))


@router.patch("/{post_id}", response_model=PostPublic)
def update_post(post_id: int, data: PostUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = PostService(db).update(post_id, user, data)
    db.commit()
    return PostService.to_public(post, include_location=True)


@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    PostService(db).delete(post_id, user)
    db.commit()
