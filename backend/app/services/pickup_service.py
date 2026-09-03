from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ForbiddenError,
    IllegalTransitionError,
    NotFoundError,
    PickupNotAssignedError,
)
from app.models.enums import (
    MatchStatusEnum,
    MaterialStatusEnum,
    NotificationTypeEnum,
    PickupStatusEnum,
)
from app.models.models import Match, Pickup, User
from app.repositories.repos import PickupRepository
from app.schemas.schemas import PickupCreate, PickupPublic, ReplacementCandidate
from app.services.notification_service import notify
from app.utils.distance import haversine_km

VALID_TRANSITIONS: dict[str, set[str]] = {
    PickupStatusEnum.PENDING.value: {PickupStatusEnum.ASSIGNED.value, PickupStatusEnum.CANCELLED.value},
    PickupStatusEnum.ASSIGNED.value: {PickupStatusEnum.ACCEPTED.value, PickupStatusEnum.CANCELLED.value},
    PickupStatusEnum.ACCEPTED.value: {PickupStatusEnum.ON_ROUTE.value, PickupStatusEnum.CANCELLED.value},
    PickupStatusEnum.ON_ROUTE.value: {PickupStatusEnum.PICKED_UP.value, PickupStatusEnum.CANCELLED.value},
    PickupStatusEnum.PICKED_UP.value: {PickupStatusEnum.DELIVERED.value, PickupStatusEnum.CANCELLED.value},
    PickupStatusEnum.DELIVERED.value: set(),
    PickupStatusEnum.CANCELLED.value: set(),
}


def _validate_transition(current: str, target: str) -> None:
    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise IllegalTransitionError(f"Cannot transition from {current} to {target}")


class PickupService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PickupRepository(db)

    def create(self, creator: User, data: PickupCreate) -> Pickup:
        match = self.db.get(Match, data.match_id)
        if not match:
            raise NotFoundError("Match not found")
        if match.status != MatchStatusEnum.ACCEPTED.value:
            raise IllegalTransitionError("Match must be ACCEPTED to create a pickup")
        material = match.material
        need = match.need
        if not material or not need:
            raise NotFoundError("Material or need not found")
        collector = self.db.get(User, data.collector_id)
        if not collector:
            raise NotFoundError("Collector not found")
        donor = material.owner
        org = need.organization
        if not donor or not org:
            raise NotFoundError("Donor or organization not found")
        pickup = self.repo.create(
            match_id=match.id,
            collector_id=collector.id,
            donor_id=donor.id,
            organization_id=org.id,
            scheduled_at=data.scheduled_at,
            pickup_address=data.pickup_address,
            delivery_address=data.delivery_address,
            notes=data.notes,
            status=PickupStatusEnum.ASSIGNED.value,
        )
        notify(
            self.db,
            collector.id,
            NotificationTypeEnum.COLLECTOR_ASSIGNED,
            "Retiro asignado",
            f"Se te ha asignado un retiro para el material '{material.name}'.",
        )
        notify(
            self.db,
            donor.id,
            NotificationTypeEnum.COLLECTOR_ASSIGNED,
            "Recolector asignado",
            f"Un recolector ha sido asignado para retirar '{material.name}'.",
        )
        return pickup

    def get(self, pickup_id: int) -> Pickup:
        pickup = self.repo.get(pickup_id)
        if not pickup:
            raise NotFoundError("Pickup not found")
        return pickup

    def list_for_user(self, user_id: int) -> list[Pickup]:
        return list(self.repo.list_by_user(user_id))

    def _transition(self, pickup: Pickup, target: str, actor: User) -> Pickup:
        _validate_transition(pickup.status, target)
        pickup.status = target
        self.db.flush()
        self.db.refresh(pickup)
        return pickup

    def accept(self, pickup_id: int, user: User) -> Pickup:
        pickup = self.get(pickup_id)
        if pickup.collector_id != user.id and user.role.value != "ADMIN":
            raise ForbiddenError("Only the assigned collector can accept")
        return self._transition(pickup, PickupStatusEnum.ACCEPTED.value, user)

    def start(self, pickup_id: int, user: User) -> Pickup:
        pickup = self.get(pickup_id)
        if pickup.collector_id != user.id and user.role.value != "ADMIN":
            raise ForbiddenError("Only the assigned collector can start")
        result = self._transition(pickup, PickupStatusEnum.ON_ROUTE.value, user)
        notify(self.db, pickup.donor_id, NotificationTypeEnum.COLLECTOR_ASSIGNED, "Recolector en ruta", "El recolector está en camino.")
        return result

    def pickup(self, pickup_id: int, user: User) -> Pickup:
        pickup = self.get(pickup_id)
        if pickup.collector_id != user.id and user.role.value != "ADMIN":
            raise ForbiddenError("Only the assigned collector can mark as picked up")
        result = self._transition(pickup, PickupStatusEnum.PICKED_UP.value, user)
        material = pickup.match.material
        if material:
            material.status = MaterialStatusEnum.PICKED_UP.value
            self.db.flush()
        notify(self.db, pickup.donor_id, NotificationTypeEnum.MATERIAL_PICKED_UP, "Material recogido", "Tu material ha sido recogido.")
        return result

    def deliver(self, pickup_id: int, user: User) -> Pickup:
        pickup = self.get(pickup_id)
        if pickup.collector_id != user.id and user.role.value != "ADMIN":
            raise ForbiddenError("Only the assigned collector can deliver")
        result = self._transition(pickup, PickupStatusEnum.DELIVERED.value, user)
        material = pickup.match.material
        if material:
            material.status = MaterialStatusEnum.DELIVERED.value
            self.db.flush()
        match = pickup.match
        if match:
            match.status = MatchStatusEnum.COMPLETED.value
            self.db.flush()
        from app.models.models import Organization
        org = self.db.get(Organization, pickup.organization_id)
        if org:
            notify(self.db, org.owner_id, NotificationTypeEnum.MATERIAL_DELIVERED, "Material entregado", "El material ha sido entregado a la organización.")
        notify(self.db, pickup.donor_id, NotificationTypeEnum.MATERIAL_DELIVERED, "Material entregado", "El material ha sido entregado a la organización.")
        return result

    def cancel(self, pickup_id: int, user: User) -> Pickup:
        pickup = self.get(pickup_id)
        if pickup.collector_id != user.id and pickup.donor_id != user.id and user.role.value != "ADMIN":
            raise ForbiddenError("Not authorized to cancel this pickup")
        result = self._transition(pickup, PickupStatusEnum.CANCELLED.value, user)
        material = pickup.match.material
        if material and material.status == MaterialStatusEnum.PICKED_UP.value:
            material.status = MaterialStatusEnum.AVAILABLE.value
            self.db.flush()
        notify(self.db, pickup.donor_id, NotificationTypeEnum.COLLECTOR_CANCELLED, "Retiro cancelado", "El recolector ha cancelado. Se buscará un reemplazo.")
        return result

    def find_replacement_collectors(
        self,
        pickup_id: int,
        max_results: int = 10,
    ) -> list[ReplacementCandidate]:
        pickup = self.get(pickup_id)
        material = pickup.match.material
        if not material:
            raise NotFoundError("Material not found for this pickup")
        from app.services.collector_service import CollectorService
        cs = CollectorService(self.db)
        origin_lat = None
        origin_lon = None
        donor = self.db.get(User, pickup.donor_id)
        if donor:
            origin_lat = donor.latitude
            origin_lon = donor.longitude
        candidates = cs.list_available(
            material_category=material.category,
            min_capacity_kg=material.estimated_weight_kg,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
        )
        results: list[ReplacementCandidate] = []
        for c in candidates:
            if c.user_id == pickup.collector_id:
                continue
            results.append(
                ReplacementCandidate(
                    collector_id=c.user_id,
                    user_name=c.user_name,
                    vehicle_type=c.vehicle_type,
                    max_weight_kg=c.max_weight_kg,
                    radius_km=c.radius_km,
                    distance_km=c.distance_km,
                    materials_accepted=c.materials_accepted,
                )
            )
            if len(results) >= max_results:
                break
        return results

    @staticmethod
    def to_public(pickup: Pickup) -> PickupPublic:
        return PickupPublic.model_validate(pickup)
