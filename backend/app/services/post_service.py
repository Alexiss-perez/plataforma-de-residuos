from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import RoleEnum
from app.models.models import Post, User
from app.repositories.repos import PostRepository
from app.schemas.schemas import PostCreate, PostPublic, PostUpdate


class PostService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PostRepository(db)

    def create(self, author: User, data: PostCreate) -> Post:
        post = self.repo.create(
            author_id=author.id,
            type=data.type.value,
            title=data.title,
            description=data.description,
            latitude=data.latitude,
            longitude=data.longitude,
            commune=data.commune,
            status=data.status.value,
        )
        return post

    def get(self, post_id: int) -> Post:
        post = self.repo.get(post_id)
        if not post:
            raise NotFoundError("Post not found")
        return post

    def list_filtered(self, skip: int = 0, limit: int = 50, **filters) -> list[Post]:
        clean = {}
        for k, v in filters.items():
            if v is not None:
                if k == "type" and hasattr(v, "value"):
                    clean[k] = v.value
                elif k == "status" and hasattr(v, "value"):
                    clean[k] = v.value
                else:
                    clean[k] = v
        return list(self.repo.list_filtered(skip, limit, **clean))

    def update(self, post_id: int, user: User, data: PostUpdate) -> Post:
        post = self.get(post_id)
        if post.author_id != user.id and user.role != RoleEnum.ADMIN:
            raise ForbiddenError("Only the author or admin can update this post")
        fields = data.model_dump(exclude_unset=True)
        for key in ("type", "status"):
            if key in fields and fields[key] is not None and hasattr(fields[key], "value"):
                fields[key] = fields[key].value
        return self.repo.update(post, fields)

    def delete(self, post_id: int, user: User) -> None:
        post = self.get(post_id)
        if post.author_id != user.id and user.role != RoleEnum.ADMIN:
            raise ForbiddenError("Only the author or admin can delete this post")
        self.repo.delete(post)

    @staticmethod
    def to_public(post: Post, include_location: bool = False) -> PostPublic:
        data = PostPublic.model_validate(post)
        if not include_location:
            data.latitude = None
            data.longitude = None
        return data
