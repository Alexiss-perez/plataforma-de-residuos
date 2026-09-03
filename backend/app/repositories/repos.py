from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Material, Match, Need, Organization, Post, Project, Pickup, Impact, Notification, CollectorProfile


class BaseRepo:
    model: type = None

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, item_id: int):
        return self.db.get(self.model, item_id)

    def create(self, **fields: Any):
        obj = self.model(**fields)
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def update(self, obj, fields: dict[str, Any]):
        for key, value in fields.items():
            setattr(obj, key, value)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def delete(self, obj) -> None:
        self.db.delete(obj)
        self.db.flush()


class CollectorProfileRepository(BaseRepo):
    model = CollectorProfile

    def get_by_user(self, user_id: int) -> CollectorProfile | None:
        return self.db.scalar(select(CollectorProfile).where(CollectorProfile.user_id == user_id))

    def list_available(self) -> Sequence[CollectorProfile]:
        return self.db.scalars(select(CollectorProfile).where(CollectorProfile.available.is_(True))).all()


class OrganizationRepository(BaseRepo):
    model = Organization

    def get_by_owner(self, owner_id: int) -> Organization | None:
        return self.db.scalar(select(Organization).where(Organization.owner_id == owner_id))

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Organization]:
        return self.db.scalars(select(Organization).offset(skip).limit(limit)).all()


class PostRepository(BaseRepo):
    model = Post

    def list_filtered(self, skip: int = 0, limit: int = 50, **filters: Any) -> Sequence[Post]:
        stmt = select(Post).order_by(Post.created_at.desc())
        for key, value in filters.items():
            if value is not None and hasattr(Post, key):
                stmt = stmt.where(getattr(Post, key) == value)
        return self.db.scalars(stmt.offset(skip).limit(limit)).all()


class MaterialRepository(BaseRepo):
    model = Material

    def list_filtered(self, skip: int = 0, limit: int = 50, **filters: Any) -> Sequence[Material]:
        stmt = select(Material).order_by(Material.created_at.desc())
        for key, value in filters.items():
            if value is not None and hasattr(Material, key):
                stmt = stmt.where(getattr(Material, key) == value)
        return self.db.scalars(stmt.offset(skip).limit(limit)).all()

    def list_by_owner(self, owner_id: int) -> Sequence[Material]:
        return self.db.scalars(select(Material).where(Material.owner_id == owner_id)).all()


class ProjectRepository(BaseRepo):
    model = Project

    def list_by_organization(self, org_id: int) -> Sequence[Project]:
        return self.db.scalars(select(Project).where(Project.organization_id == org_id)).all()

    def list_all(self, skip: int = 0, limit: int = 50) -> Sequence[Project]:
        return self.db.scalars(select(Project).offset(skip).limit(limit)).all()


class NeedRepository(BaseRepo):
    model = Need

    def list_filtered(self, skip: int = 0, limit: int = 50, **filters: Any) -> Sequence[Need]:
        stmt = select(Need).order_by(Need.created_at.desc())
        for key, value in filters.items():
            if value is not None and hasattr(Need, key):
                stmt = stmt.where(getattr(Need, key) == value)
        return self.db.scalars(stmt.offset(skip).limit(limit)).all()

    def list_open(self) -> Sequence[Need]:
        return self.db.scalars(select(Need).where(Need.status.in_(["OPEN", "PARTIALLY_FILLED"]))).all()


class MatchRepository(BaseRepo):
    model = Match

    def list_by_material(self, material_id: int) -> Sequence[Match]:
        return self.db.scalars(select(Match).where(Match.material_id == material_id).order_by(Match.score.desc())).all()

    def list_by_need(self, need_id: int) -> Sequence[Match]:
        return self.db.scalars(select(Match).where(Match.need_id == need_id).order_by(Match.score.desc())).all()


class PickupRepository(BaseRepo):
    model = Pickup

    def list_by_collector(self, collector_id: int) -> Sequence[Pickup]:
        return self.db.scalars(select(Pickup).where(Pickup.collector_id == collector_id).order_by(Pickup.created_at.desc())).all()

    def list_by_user(self, user_id: int) -> Sequence[Pickup]:
        return self.db.scalars(
            select(Pickup).where((Pickup.collector_id == user_id) | (Pickup.donor_id == user_id)).order_by(Pickup.created_at.desc())
        ).all()

    def get_active_by_match(self, match_id: int) -> Pickup | None:
        return self.db.scalar(
            select(Pickup).where(Pickup.match_id == match_id, Pickup.status != "CANCELLED").order_by(Pickup.created_at.desc())
        )


class ImpactRepository(BaseRepo):
    model = Impact

    def list_all(self, skip: int = 0, limit: int = 100) -> Sequence[Impact]:
        return self.db.scalars(select(Impact).order_by(Impact.created_at.desc()).offset(skip).limit(limit)).all()

    def list_by_organization(self, org_id: int) -> Sequence[Impact]:
        return self.db.scalars(select(Impact).where(Impact.organization_id == org_id)).all()


class NotificationRepository(BaseRepo):
    model = Notification

    def list_by_user(self, user_id: int) -> Sequence[Notification]:
        return self.db.scalars(select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())).all()
