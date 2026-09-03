from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import MaterialCreate, MaterialPublic, MaterialUpdate
from app.services.material_service import MaterialService

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.post("", response_model=MaterialPublic, status_code=201)
def create(data: MaterialCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    material = MaterialService(db).create(user, data)
    db.commit()
    return MaterialService.to_public(material)


@router.get("", response_model=list[MaterialPublic])
def list_materials(
    category: str | None = None,
    status: str | None = None,
    commune: str | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return [MaterialService.to_public(m) for m in MaterialService(db).list_filtered(skip, limit, category=category, status=status)]


@router.get("/{material_id}", response_model=MaterialPublic)
def get_one(material_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return MaterialService.to_public(MaterialService(db).get(material_id))


@router.patch("/{material_id}", response_model=MaterialPublic)
def update(material_id: int, data: MaterialUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    material = MaterialService(db).update(material_id, user, data)
    db.commit()
    return MaterialService.to_public(material)
