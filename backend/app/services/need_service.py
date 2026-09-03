from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import RoleEnum
from app.models.models import Need, User
from app.repositories.repos import NeedRepository
from app.schemas.schemas import NeedCreate, NeedPublic, NeedUpdate


class NeedService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = NeedRepository(db)

    def _get_org_of(self, user: User):
        from app.repositories.repos import OrganizationRepository
        return OrganizationRepository(self.db).get_by_owner(user.id)

    def create(self, user: User, data: NeedCreate) -> Need:
        org = self._get_org_of(user)
        if not org:
            raise ForbiddenError("Only organizations can create needs")
        need = self.repo.create(
            organization_id=org.id,
            project_id=data.project_id,
            material_category=data.material_category.value,
            material_name=data.material_name,
            description=data.description,
            quantity_required=data.quantity_required,
            quantity_received=0,
            unit=data.unit,
            priority=data.priority.value,
            status="OPEN",
        )
        return need

    def get(self, need_id: int) -> Need:
        need = self.repo.get(need_id)
        if not need:
            raise NotFoundError("Need not found")
        return need

    def list_filtered(self, skip: int = 0, limit: int = 50, **filters) -> list[Need]:
        clean = {}
        for k, v in filters.items():
            if v is not None:
                if hasattr(v, "value"):
                    clean[k] = v.value
                else:
                    clean[k] = v
        return list(self.repo.list_filtered(skip, limit, **clean))

    def update(self, need_id: int, user: User, data: NeedUpdate) -> Need:
        need = self.get(need_id)
        org = self._get_org_of(user)
        if (not org or org.id != need.organization_id) and user.role != RoleEnum.ADMIN:
            raise ForbiddenError("Only the organization owner or admin can update this need")
        fields = data.model_dump(exclude_unset=True)
        if "priority" in fields and fields["priority"] is not None and hasattr(fields["priority"], "value"):
            fields["priority"] = fields["priority"].value
        return self.repo.update(need, fields)

    @staticmethod
    def to_public(need: Need) -> NeedPublic:
        return NeedPublic.model_validate(need)
