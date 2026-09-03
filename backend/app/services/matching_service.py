from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ForbiddenError,
    HazardousMaterialError,
    MaterialNotAvailableError,
    NeedClosedError,
    NotFoundError,
)
from app.models.enums import (
    MatchStatusEnum,
    MaterialStatusEnum,
    NeedStatusEnum,
    NotificationTypeEnum,
)
from app.models.models import Match, Material, Need, User
from app.repositories.repos import MatchRepository, MaterialRepository, NeedRepository
from app.schemas.schemas import MatchGenerateResponse, MatchPublic
from app.services.notification_service import notify
from app.utils.distance import distance_score, haversine_km
from app.utils.hazardous import is_hazardous

WEIGHTS = {
    "material": 0.40,
    "quantity": 0.20,
    "distance": 0.20,
    "priority": 0.10,
    "condition": 0.10,
}

PRIORITY_SCORES = {
    "URGENT": 100.0,
    "HIGH": 80.0,
    "MEDIUM": 60.0,
    "LOW": 40.0,
}

CONDITION_SCORES = {
    "NEW": 100.0,
    "GOOD": 90.0,
    "REUSABLE": 80.0,
    "REPAIRABLE": 50.0,
    "RECYCLE_ONLY": 30.0,
    "UNKNOWN": 60.0,
}


def _material_score(material: Material, need: Need) -> float:
    if material.category.upper() == need.material_category.upper():
        return 100.0
    return 0.0


def _quantity_score(material: Material, need: Need) -> float:
    if material.quantity <= 0:
        return 0.0
    if material.quantity >= need.quantity_required:
        return 100.0
    ratio = material.quantity / need.quantity_required
    return round(ratio * 100.0, 2)


def _get_material_location(material: Material) -> tuple[float | None, float | None]:
    if material.post and material.post.latitude is not None and material.post.longitude is not None:
        return material.post.latitude, material.post.longitude
    if material.owner and material.owner.latitude is not None and material.owner.longitude is not None:
        return material.owner.latitude, material.owner.longitude
    return None, None


def _distance_score(material: Material, need: Need) -> float:
    mlat, mlon = _get_material_location(material)
    if mlat is None or mlon is None:
        return 50.0
    org = need.organization
    if org is None or org.latitude is None or org.longitude is None:
        return 50.0
    dist = haversine_km(mlat, mlon, org.latitude, org.longitude)
    return round(distance_score(dist), 2)


def _priority_score(need: Need) -> float:
    return PRIORITY_SCORES.get(need.priority, 60.0)


def _condition_score(material: Material) -> float:
    return CONDITION_SCORES.get(material.condition, 60.0)


def compute_match(material: Material, need: Need) -> dict[str, float]:
    ms = _material_score(material, need)
    qs = _quantity_score(material, need)
    ds = _distance_score(material, need)
    ps = _priority_score(need)
    cs = _condition_score(material)
    final = (
        WEIGHTS["material"] * ms
        + WEIGHTS["quantity"] * qs
        + WEIGHTS["distance"] * ds
        + WEIGHTS["priority"] * ps
        + WEIGHTS["condition"] * cs
    )
    return {
        "score": round(final, 2),
        "material_score": ms,
        "quantity_score": qs,
        "distance_score": ds,
        "priority_score": ps,
        "condition_score": cs,
    }


class MatchingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.match_repo = MatchRepository(db)
        self.material_repo = MaterialRepository(db)
        self.need_repo = NeedRepository(db)

    def generate_for_material(self, material_id: int) -> list[Match]:
        material = self.material_repo.get(material_id)
        if not material:
            raise NotFoundError("Material not found")
        if material.status != MaterialStatusEnum.AVAILABLE.value:
            raise MaterialNotAvailableError("Material is not available for matching")
        if is_hazardous(material.category, material.name, material.description) or material.risk_level == "SPECIAL_HANDLING":
            raise HazardousMaterialError("Hazardous materials cannot be matched automatically")

        open_needs = self.need_repo.list_open()
        created: list[Match] = []
        for need in open_needs:
            scores = compute_match(material, need)
            if scores["material_score"] == 0:
                continue
            reason = self._build_reason(material, need, scores)
            match = self.match_repo.create(
                material_id=material.id,
                need_id=need.id,
                status=MatchStatusEnum.PROPOSED.value,
                reason=reason,
                **scores,
            )
            created.append(match)
            org = need.organization
            if org:
                notify(
                    self.db,
                    org.owner_id,
                    NotificationTypeEnum.MATCH_FOUND,
                    "Nuevo match encontrado",
                    f"Se encontró un match ({scores['score']}/100) entre '{material.name}' y una necesidad de tu organización.",
                )
        return created

    def _build_reason(self, material: Material, need: Need, scores: dict[str, float]) -> str:
        parts = [f"Score global: {scores['score']}/100."]
        parts.append(f"Material compatible ({material.category} ↔ {need.material_category}).")
        parts.append(f"Cantidad: {material.quantity} {material.unit} disponibles vs {need.quantity_required} {need.unit} requeridos.")
        parts.append(f"Condición del material: {material.condition}.")
        parts.append(f"Prioridad de la necesidad: {need.priority}.")
        return " ".join(parts)

    def list_by_material(self, material_id: int) -> list[Match]:
        return list(self.match_repo.list_by_material(material_id))

    def list_by_need(self, need_id: int) -> list[Match]:
        return list(self.match_repo.list_by_need(need_id))

    def accept(self, match_id: int, user: User) -> Match:
        match = self.match_repo.get(match_id)
        if not match:
            raise NotFoundError("Match not found")
        if match.status != MatchStatusEnum.PROPOSED.value:
            raise MaterialNotAvailableError("Match is not in PROPOSED state")
        material = match.material
        need = match.need
        org = need.organization
        is_owner = material.owner_id == user.id
        is_org_owner = org and org.owner_id == user.id
        is_admin = user.role.value == "ADMIN"
        if not (is_owner or is_org_owner or is_admin):
            raise ForbiddenError("Only the material owner or organization owner can accept this match")
        if material.status != MaterialStatusEnum.AVAILABLE.value:
            raise MaterialNotAvailableError("Material is no longer available")
        if need.status not in (NeedStatusEnum.OPEN.value, NeedStatusEnum.PARTIALLY_FILLED.value):
            raise NeedClosedError("Need is no longer open")
        match.status = MatchStatusEnum.ACCEPTED.value
        material.status = MaterialStatusEnum.MATCHED.value
        delivered_qty = min(material.quantity, need.quantity_required - need.quantity_received)
        need.quantity_received += delivered_qty
        if need.quantity_received >= need.quantity_required:
            need.status = NeedStatusEnum.FULFILLED.value
        elif need.quantity_received > 0:
            need.status = NeedStatusEnum.PARTIALLY_FILLED.value
        self.db.flush()
        self.db.refresh(match)
        notify(
            self.db,
            material.owner_id,
            NotificationTypeEnum.MATCH_ACCEPTED,
            "Match aceptado",
            f"Tu material '{material.name}' fue aceptado para una necesidad.",
        )
        if org:
            notify(
                self.db,
                org.owner_id,
                NotificationTypeEnum.MATCH_ACCEPTED,
                "Match aceptado",
                f"La organización aceptó un match para la necesidad de {need.material_category}.",
            )
        return match

    def reject(self, match_id: int, user: User) -> Match:
        match = self.match_repo.get(match_id)
        if not match:
            raise NotFoundError("Match not found")
        if match.status != MatchStatusEnum.PROPOSED.value:
            raise MaterialNotAvailableError("Match is not in PROPOSED state")
        material = match.material
        need = match.need
        org = need.organization
        is_owner = material.owner_id == user.id
        is_org_owner = org and org.owner_id == user.id
        is_admin = user.role.value == "ADMIN"
        if not (is_owner or is_org_owner or is_admin):
            raise ForbiddenError("Only the material owner or organization owner can reject this match")
        match.status = MatchStatusEnum.REJECTED.value
        self.db.flush()
        self.db.refresh(match)
        return match

    @staticmethod
    def to_public(match: Match) -> MatchPublic:
        return MatchPublic.model_validate(match)
