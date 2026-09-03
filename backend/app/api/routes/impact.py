from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import ImpactCreate, ImpactPublic, ImpactStats
from app.services.impact_service import ImpactService

router = APIRouter(prefix="/impact", tags=["Impact"])


@router.post("", response_model=ImpactPublic, status_code=201)
def create(data: ImpactCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    impact = ImpactService(db).register(user, data)
    db.commit()
    return ImpactService.to_public(impact)


@router.get("", response_model=list[ImpactPublic])
def list_all(skip: int = 0, limit: int = Query(default=100, le=500), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [ImpactService.to_public(i) for i in ImpactService(db).list_all(skip, limit)]


@router.get("/me", response_model=list[ImpactPublic])
def list_mine(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [ImpactService.to_public(i) for i in ImpactService(db).list_for_organization(user)]


@router.get("/stats", response_model=ImpactStats)
def stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ImpactService(db).stats()
