from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import NeedCreate, NeedPublic, NeedUpdate
from app.services.need_service import NeedService

router = APIRouter(prefix="/needs", tags=["Needs"])


@router.post("", response_model=NeedPublic, status_code=201)
def create(data: NeedCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    need = NeedService(db).create(user, data)
    db.commit()
    return NeedService.to_public(need)


@router.get("", response_model=list[NeedPublic])
def list_all(
    material_category: str | None = None,
    status: str | None = None,
    organization_id: int | None = None,
    project_id: int | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return [
        NeedService.to_public(n)
        for n in NeedService(db).list_filtered(
            skip, limit, material_category=material_category, status=status, organization_id=organization_id, project_id=project_id
        )
    ]


@router.get("/{need_id}", response_model=NeedPublic)
def get_one(need_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return NeedService.to_public(NeedService(db).get(need_id))


@router.patch("/{need_id}", response_model=NeedPublic)
def update(need_id: int, data: NeedUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    need = NeedService(db).update(need_id, user, data)
    db.commit()
    return NeedService.to_public(need)
