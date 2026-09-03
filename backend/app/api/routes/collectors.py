from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import (
    CollectorProfileCreate,
    CollectorProfilePublic,
    CollectorProfileUpdate,
    CollectorWithUserPublic,
)
from app.services.collector_service import CollectorService

router = APIRouter(prefix="/collectors", tags=["Collectors"])


@router.post("/profile", response_model=CollectorProfilePublic, status_code=201)
def create_profile(data: CollectorProfileCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = CollectorService(db).create_profile(user.id, data)
    db.commit()
    return CollectorService.to_public(profile)


@router.get("/profile/me", response_model=CollectorProfilePublic)
def get_my_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = CollectorService(db).get_my_profile(user.id)
    return CollectorService.to_public(profile)


@router.patch("/profile/me", response_model=CollectorProfilePublic)
def update_my_profile(data: CollectorProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = CollectorService(db).update_profile(user.id, data)
    db.commit()
    return CollectorService.to_public(profile)


@router.get("/available", response_model=list[CollectorWithUserPublic])
def list_available(
    material: str | None = Query(default=None),
    max_distance_km: float | None = Query(default=None),
    origin_lat: float | None = Query(default=None),
    origin_lon: float | None = Query(default=None),
    min_capacity_kg: float | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CollectorService(db).list_available(
        material_category=material,
        max_distance_km=max_distance_km,
        origin_lat=origin_lat,
        origin_lon=origin_lon,
        min_capacity_kg=min_capacity_kg,
    )
