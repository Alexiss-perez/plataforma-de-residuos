from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.models.enums import RoleEnum
from app.models.models import Organization, User
from app.repositories.repos import OrganizationRepository
from app.schemas.schemas import OrganizationCreate, OrganizationPublic, OrganizationUpdate


class OrganizationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrganizationRepository(db)

    def create(self, owner: User, data: OrganizationCreate) -> Organization:
        if self.repo.get_by_owner(owner.id):
            raise ConflictError("User already has an organization")
        org = self.repo.create(
            owner_id=owner.id,
            name=data.name,
            type=data.type.value,
            description=data.description,
            commune=data.commune,
            latitude=data.latitude,
            longitude=data.longitude,
        )
        if owner.role == RoleEnum.NATURAL:
            owner.role = RoleEnum.ORGANIZATION
            self.db.flush()
        return org

    def get(self, org_id: int) -> Organization:
        org = self.repo.get(org_id)
        if not org:
            raise NotFoundError("Organization not found")
        return org

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Organization]:
        return list(self.repo.list_all(skip, limit))

    def update(self, org_id: int, user: User, data: OrganizationUpdate) -> Organization:
        org = self.get(org_id)
        if org.owner_id != user.id and user.role != RoleEnum.ADMIN:
            raise ForbiddenError("Only the owner or admin can update this organization")
        fields = data.model_dump(exclude_unset=True)
        if "type" in fields and fields["type"] is not None:
            fields["type"] = fields["type"].value if hasattr(fields["type"], "value") else fields["type"]
        return self.repo.update(org, fields)

    @staticmethod
    def to_public(org: Organization) -> OrganizationPublic:
        return OrganizationPublic.model_validate(org)
