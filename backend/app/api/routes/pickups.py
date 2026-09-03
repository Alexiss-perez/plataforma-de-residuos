from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.enums import RoleEnum
from app.models.models import User
from app.schemas.schemas import PickupCreate, PickupPublic, ReplacementCandidate
from app.services.pickup_service import PickupService

router = APIRouter(prefix="/pickups", tags=["Pickups"])


def _is_participant(pickup, user: User) -> bool:
    if user.role == RoleEnum.ADMIN:
        return True
    return pickup.collector_id == user.id or pickup.donor_id == user.id or pickup.organization_id == _get_org_owner_id(pickup, user)


def _get_org_owner_id(pickup, user: User) -> int | None:
    from app.models.models import Organization
    org = user.organization
    return org.id if org else None


@router.post("", response_model=PickupPublic, status_code=201)
def create(data: PickupCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pickup = PickupService(db).create(user, data)
    db.commit()
    return PickupService.to_public(pickup)


@router.get("/me", response_model=list[PickupPublic])
def list_mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [PickupService.to_public(p) for p in PickupService(db).list_for_user(user.id)]


@router.get("/{pickup_id}", response_model=PickupPublic)
def get_one(pickup_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pickup = PickupService(db).get(pickup_id)
    is_participant = (
        user.role == RoleEnum.ADMIN
        or pickup.collector_id == user.id
        or pickup.donor_id == user.id
        or (user.organization is not None and user.organization.id == pickup.organization_id)
    )
    if not is_participant:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Only participants can view this pickup")
    return PickupService.to_public(pickup)


@router.post("/{pickup_id}/accept", response_model=PickupPublic)
def accept(pickup_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pickup = PickupService(db).accept(pickup_id, user)
    db.commit()
    return PickupService.to_public(pickup)


@router.post("/{pickup_id}/start", response_model=PickupPublic)
def start(pickup_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pickup = PickupService(db).start(pickup_id, user)
    db.commit()
    return PickupService.to_public(pickup)


@router.post("/{pickup_id}/pickup", response_model=PickupPublic)
def do_pickup(pickup_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pickup = PickupService(db).pickup(pickup_id, user)
    db.commit()
    return PickupService.to_public(pickup)


@router.post("/{pickup_id}/deliver", response_model=PickupPublic)
def deliver(pickup_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pickup = PickupService(db).deliver(pickup_id, user)
    db.commit()
    return PickupService.to_public(pickup)


@router.post("/{pickup_id}/cancel", response_model=PickupPublic)
def cancel(pickup_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pickup = PickupService(db).cancel(pickup_id, user)
    db.commit()
    return PickupService.to_public(pickup)


@router.get("/{pickup_id}/replacements", response_model=list[ReplacementCandidate])
def replacements(pickup_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return PickupService(db).find_replacement_collectors(pickup_id)
