from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.agents.llm_client import LLMClient, get_llm_client
from app.agents.prompts import (
    AMBIGUITY_SYSTEM,
    ANALYZE_MATERIAL_SYSTEM,
    CONTINGENCY_SYSTEM,
    EXPLAIN_MATCH_SYSTEM,
    INTERPRET_NEED_SYSTEM,
)
from app.agents.tools import AgentTools
from app.schemas.schemas import (
    AIMatchExplanation,
    AIMaterialAnalysis,
    AINeedInterpretation,
)
from app.utils.hazardous import determine_risk_level


class EcoMatchAgent:
    """AI agent for ReVínculo.

    Uses an LLM for natural-language understanding but ALL side effects
    go through AgentTools / services which validate against the DB.
    The agent never writes to the DB directly.
    """

    def __init__(self, db: Session, client: LLMClient | None = None) -> None:
        self.db = db
        self.client = client or get_llm_client()
        self.tools = AgentTools(db)

    def analyze_material(self, text: str) -> AIMaterialAnalysis:
        raw = self.client.chat(ANALYZE_MATERIAL_SYSTEM, f"Analiza: {text}")
        data = json.loads(raw)
        for m in data.get("materials", []):
            auto_risk = determine_risk_level(m.get("category", "OTHER"), m.get("type"), text)
            if auto_risk == "SPECIAL_HANDLING":
                m["risk_level"] = "SPECIAL_HANDLING"
        return AIMaterialAnalysis.model_validate(data)

    def interpret_need(self, text: str) -> AINeedInterpretation:
        raw = self.client.chat(INTERPRET_NEED_SYSTEM, f"Interpreta: {text}")
        data = json.loads(raw)
        return AINeedInterpretation.model_validate(data)

    def explain_match(self, material_id: int, need_id: int) -> AIMatchExplanation:
        scores = self.tools.calculate_match(material_id, need_id)
        if not scores:
            return AIMatchExplanation(score=0, reasons=["No se pudo calcular el match."], confidence=0.0)
        raw = self.client.chat(
            EXPLAIN_MATCH_SYSTEM,
            f"Material score: {scores['score']}/100. Sub-scores: {scores}. Explica brevemente.",
        )
        data = json.loads(raw)
        return AIMatchExplanation.model_validate(data)

    def detect_ambiguity(self, text: str) -> dict[str, Any]:
        raw = self.client.chat(AMBIGUITY_SYSTEM, f"Analiza ambigüedad: {text}")
        return json.loads(raw)

    def handle_contingency(self, pickup_id: int) -> dict[str, Any]:
        try:
            candidates = self.tools.find_replacement_collectors(pickup_id)
        except Exception:
            candidates = []
        if not candidates:
            return {"action": "none", "reason": "No hay recolectores disponibles.", "candidates": []}
        raw = self.client.chat(
            CONTINGENCY_SYSTEM,
            f"Pickup {pickup_id} cancelado. Candidatos: {json.dumps(candidates)}",
        )
        recommendation = json.loads(raw)
        return {"action": "recommend_replacement", "recommendation": recommendation, "candidates": candidates}

    def chat(self, message: str, context: dict | None = None) -> dict[str, Any]:
        ctx_str = json.dumps(context or {})
        raw = self.client.chat(
            "You are EcoMatchAgent. Answer concisely.",
            f"Context: {ctx_str}\nUser: {message}",
        )
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"response": raw}
