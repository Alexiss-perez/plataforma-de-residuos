from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.enums import RoleEnum
from app.models.models import Material, User
from app.repositories.repos import MaterialRepository
from app.schemas.schemas import MaterialCreate, MaterialPublic, MaterialUpdate
from app.utils.hazardous import determine_risk_level, is_hazardous


class MaterialService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = MaterialRepository(db)

    def create(self, owner: User, data: MaterialCreate) -> Material:
        risk = data.risk_level.value
        auto_risk = determine_risk_level(data.category.value, data.name, data.description)
        if auto_risk == "SPECIAL_HANDLING":
            risk = "SPECIAL_HANDLING"
        material = self.repo.create(
            post_id=data.post_id,
            owner_id=owner.id,
            name=data.name,
            category=data.category.value,
            description=data.description,
            quantity=data.quantity,
            unit=data.unit,
            condition=data.condition.value,
            estimated_weight_kg=data.estimated_weight_kg,
            risk_level=risk,
            requires_pickup=data.requires_pickup,
            status="AVAILABLE",
        )
        return material

    def get(self, material_id: int) -> Material:
        material = self.repo.get(material_id)
        if not material:
            raise NotFoundError("Material not found")
        return material

    def list_filtered(self, skip: int = 0, limit: int = 50, **filters) -> list[Material]:
        clean = {}
        for k, v in filters.items():
            if v is not None:
                if hasattr(v, "value"):
                    clean[k] = v.value
                else:
                    clean[k] = v
        return list(self.repo.list_filtered(skip, limit, **clean))

    def update(self, material_id: int, user: User, data: MaterialUpdate) -> Material:
        material = self.get(material_id)
        if material.owner_id != user.id and user.role != RoleEnum.ADMIN:
            raise ForbiddenError("Only the owner or admin can update this material")
        fields = data.model_dump(exclude_unset=True)
        for key in ("category", "condition", "risk_level"):
            if key in fields and fields[key] is not None and hasattr(fields[key], "value"):
                fields[key] = fields[key].value
        return self.repo.update(material, fields)

    @staticmethod
    def to_public(material: Material) -> MaterialPublic:
        return MaterialPublic.model_validate(material)
