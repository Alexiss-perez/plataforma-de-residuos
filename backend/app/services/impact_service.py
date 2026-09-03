from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import MatchStatusEnum, MaterialStatusEnum, NotificationTypeEnum
from app.models.models import Impact, Match, Organization, Pickup, User
from app.repositories.repos import ImpactRepository
from app.schemas.schemas import ImpactCreate, ImpactPublic, ImpactStats
from app.services.notification_service import notify


class ImpactService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ImpactRepository(db)

    def register(self, user: User, data: ImpactCreate) -> Impact:
        match = self.db.get(Match, data.match_id)
        if not match:
            raise NotFoundError("Match not found")
        org = match.need.organization if match.need else None
        if not org:
            raise NotFoundError("Organization not found for this match")
        if org.owner_id != user.id and user.role.value != "ADMIN":
            raise ForbiddenError("Only the organization owner can register impact")
        impact = self.repo.create(
            match_id=match.id,
            organization_id=org.id,
            description=data.description,
            final_use=data.final_use,
            weight_reused_kg=data.weight_reused_kg,
            people_benefited=data.people_benefited,
            image_url=data.image_url,
        )
        material = match.material
        if material:
            material.status = MaterialStatusEnum.REUSED.value
            self.db.flush()
        notify(
            self.db,
            material.owner_id if material else org.owner_id,
            NotificationTypeEnum.IMPACT_REGISTERED,
            "Impacto registrado",
            f"La organización registró el impacto: {data.final_use or 'reutilización'}.",
        )
        return impact

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Impact]:
        return list(self.repo.list_all(skip, limit))

    def list_for_organization(self, user: User) -> list[Impact]:
        from app.repositories.repos import OrganizationRepository
        org = OrganizationRepository(self.db).get_by_owner(user.id)
        if not org:
            raise NotFoundError("Organization not found")
        return list(self.repo.list_by_organization(org.id))

    def stats(self) -> ImpactStats:
        total_weight = self.db.scalar(select(func.coalesce(func.sum(Impact.weight_reused_kg), 0.0))) or 0.0
        total_deliveries = self.db.scalar(
            select(func.count(Pickup.id)).where(Pickup.status == "DELIVERED")
        ) or 0
        total_materials = self.db.scalar(
            select(func.count(Impact.id))
        ) or 0
        orgs_helped = self.db.scalar(
            select(func.count(func.distinct(Impact.organization_id)))
        ) or 0
        donors_ids = self.db.scalars(
            select(func.distinct(Match.material_id)).where(Match.status == MatchStatusEnum.COMPLETED.value)
        ).all()
        donors_count = len(donors_ids)
        collectors_count = self.db.scalar(
            select(func.count(func.distinct(Pickup.collector_id))).where(Pickup.status == "DELIVERED")
        ) or 0
        return ImpactStats(
            total_weight_reused_kg=round(float(total_weight), 2),
            total_deliveries=int(total_deliveries),
            total_materials=int(total_materials),
            organizations_helped=int(orgs_helped),
            donors_count=int(donors_count),
            collectors_count=int(collectors_count),
        )

    @staticmethod
    def to_public(impact: Impact) -> ImpactPublic:
        return ImpactPublic.model_validate(impact)
