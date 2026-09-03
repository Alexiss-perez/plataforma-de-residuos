from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.ecomatch_agent import EcoMatchAgent
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import (
    AIChatRequest,
    AIChatResponse,
    AIMatchExplanation,
    AIMaterialAnalysis,
    AINeedInterpretation,
)

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/analyze-material", response_model=AIMaterialAnalysis)
def analyze_material(req: AIChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return EcoMatchAgent(db).analyze_material(req.message)


@router.post("/interpret-need", response_model=AINeedInterpretation)
def interpret_need(req: AIChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return EcoMatchAgent(db).interpret_need(req.message)


@router.post("/explain-match", response_model=AIMatchExplanation)
def explain_match(material_id: int, need_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return EcoMatchAgent(db).explain_match(material_id, need_id)


@router.post("/contingency")
def contingency(pickup_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return EcoMatchAgent(db).handle_contingency(pickup_id)


@router.post("/chat", response_model=AIChatResponse)
def chat(req: AIChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = EcoMatchAgent(db).chat(req.message, req.context)
    return AIChatResponse(
        response=str(result.get("response", "")),
        action=result.get("action"),
        data=result.get("data"),
    )
