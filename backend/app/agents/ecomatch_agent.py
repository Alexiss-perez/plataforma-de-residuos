from __future__ import annotations

import json
from typing import Any, Generator

from sqlalchemy.orm import Session

from app.agents.llm_client import LLMClient, get_llm_client
from app.agents.prompts import (
    AMBIGUITY_SYSTEM,
    ANALYZE_MATERIAL_SYSTEM,
    CHAT_SYSTEM_PROMPT,
    CONTINGENCY_SYSTEM,
    EXPLAIN_MATCH_SYSTEM,
    INTERPRET_NEED_SYSTEM,
)
from app.agents.guardrail import validar_respuesta
from app.agents.tools import AgentTools
from app.schemas.schemas import (
    AIMatchExplanation,
    AIMaterialAnalysis,
    AINeedInterpretation,
)
from app.utils.hazardous import determine_risk_level


class EcoMatchAgent:
    """Agente IA unificado para EcoMatch / ReVínculo.

    Dos modos de operación:
    1. Programático: analyze_material, interpret_need, explain_match, etc.
       (para endpoints REST del backend)
    2. Conversacional: chat, chat_stream
       (para WebSocket del frontend — streaming token a token)

    En ambos modos, el LLM nunca escribe directamente en la DB.
    Toda acción pasa por AgentTools → services → validaciones.
    """

    def __init__(self, db: Session, client: LLMClient | None = None) -> None:
        self.db = db
        self.client = client or get_llm_client()
        self.tools = AgentTools(db)

    # ── Modo programático (REST /api/v1/ai/*) ──────────────────────────────

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

    # ── Modo conversacional (WebSocket /ws) ────────────────────────────────

    def chat(self, message: str, context: dict | None = None) -> dict[str, Any]:
        """Chat conversacional usando el system prompt avanzado."""
        ctx_str = json.dumps(context or {})
        raw = self.client.chat(
            CHAT_SYSTEM_PROMPT,
            f"Context: {ctx_str}\nUser: {message}",
            response_format_json=False,
        )

        # Guardrail: validar antes de devolver
        validacion = validar_respuesta(raw)
        guardrail_blocked = not validacion["ok"]
        if guardrail_blocked:
            raw = validacion["mensaje_alternativo"]

        return {"response": raw, "guardrail_blocked": guardrail_blocked}

    def chat_stream(self, message: str, context: dict | None = None) -> Generator[dict, None, None]:
        """
        Chat conversacional con streaming token a token.
        Genera (yield) eventos:
            {"type": "token", "content": "..."}
            {"type": "done", "content": "..."}
            {"type": "guardrail_blocked", "razon": "..."}
        """
        ctx_str = json.dumps(context or {})
        raw = self.client.chat(
            CHAT_SYSTEM_PROMPT,
            f"Context: {ctx_str}\nUser: {message}",
            response_format_json=False,
        )

        # Simular streaming dividiendo la respuesta en chunks
        chunk_size = 5
        for i in range(0, len(raw), chunk_size):
            chunk = raw[i:i + chunk_size]
            yield {"type": "token", "content": chunk}

        # Guardrail
        validacion = validar_respuesta(raw)
        if not validacion["ok"]:
            yield {"type": "guardrail_blocked", "razon": validacion["razon"]}
            yield {"type": "done", "content": validacion["mensaje_alternativo"]}
        else:
            yield {"type": "done", "content": raw}
