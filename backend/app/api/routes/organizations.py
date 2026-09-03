from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import OrganizationCreate, OrganizationPublic, OrganizationUpdate
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post("", response_model=OrganizationPublic, status_code=201)
def create(data: OrganizationCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = OrganizationService(db).create(user, data)
    db.commit()
    return OrganizationService.to_public(org)


@router.get("", response_model=list[OrganizationPublic])
def list_all(skip: int = 0, limit: int = Query(default=100, le=500), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [OrganizationService.to_public(o) for o in OrganizationService(db).list_all(skip, limit)]


@router.get("/{org_id}", response_model=OrganizationPublic)
def get_one(org_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return OrganizationService.to_public(OrganizationService(db).get(org_id))


@router.patch("/{org_id}", response_model=OrganizationPublic)
def update(org_id: int, data: OrganizationUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = OrganizationService(db).update(org_id, user, data)
    db.commit()
    return OrganizationService.to_public(org)
