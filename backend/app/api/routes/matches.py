from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import MatchGenerateResponse, MatchPublic
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post("/generate/{material_id}", response_model=MatchGenerateResponse)
def generate(material_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = MatchingService(db).generate_for_material(material_id)
    db.commit()
    return MatchGenerateResponse(material_id=material_id, matches=[MatchingService.to_public(m) for m in matches])


@router.get("/material/{material_id}", response_model=list[MatchPublic])
def by_material(material_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [MatchingService.to_public(m) for m in MatchingService(db).list_by_material(material_id)]


@router.get("/need/{need_id}", response_model=list[MatchPublic])
def by_need(need_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [MatchingService.to_public(m) for m in MatchingService(db).list_by_need(need_id)]


@router.post("/{match_id}/accept", response_model=MatchPublic)
def accept(match_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    match = MatchingService(db).accept(match_id, user)
    db.commit()
    return MatchingService.to_public(match)


@router.post("/{match_id}/reject", response_model=MatchPublic)
def reject(match_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    match = MatchingService(db).reject(match_id, user)
    db.commit()
    return MatchingService.to_public(match)
