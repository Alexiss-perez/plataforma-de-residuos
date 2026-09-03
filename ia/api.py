"""
API REST del Agente EcoMatch — FastAPI
=======================================
Expone el agente de IA para que el Frontend y Backend se conecten via HTTP.

Endpoints:
    POST /chat          — envía mensaje al agente, devuelve respuesta
    POST /chat/reset    — reinicia la conversación
    GET  /health        — health check

Uso:
    uvicorn api:app --reload --port 8000
"""
import os
import sys
import uuid
import json
import logging
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Imports del agente ──────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from ecomatch_agent import enviar_mensaje, SYSTEM_PROMPT
from guardrail import validar_respuesta

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "agent.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ecomatch")

# ── Sesiones en memoria (en producción: Redis) ─────────────────────────────
sesiones: dict[str, list] = {}

# ── FastAPI ─────────────────────────────────────────────────────────────────
app = FastAPI(title="EcoMatch AI Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WELCOME_MSG = (
    "👋 ¡Hola! Soy **EcoMatch**, tu agente de economía circular. ♻️\n\n"
    "Puedo ayudarte a:\n"
    "1. **Publicar residuos** que quieres que retiren de tu ubicación\n"
    "2. **Buscar receptores** cerca de ti (ONGs, plantas de reciclaje, pymes)\n"
    "3. **Coordinar el retiro** entre tú y el receptor\n\n"
    "Cuéntame: ¿qué residuo tienes y dónde estás ubicado?"
)


# ── Models ──────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    tool_calls: list = []
    timestamp: str


# ── Endpoints ───────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "glm-5.2", "timestamp": datetime.now().isoformat()}


@app.post("/chat")
def chat(req: ChatRequest) -> ChatResponse:
    """Endpoint principal: envía un mensaje al agente y devuelve la respuesta."""
    session_id = req.session_id or str(uuid.uuid4())

    if session_id not in sesiones:
        sesiones[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        logger.info(f"Nueva sesión: {session_id}")

    if req.message.lower().strip() in ("hola", "hi", "hello", "inicio"):
        return ChatResponse(
            session_id=session_id,
            response=WELCOME_MSG,
            timestamp=datetime.now().isoformat(),
        )

    messages = sesiones[session_id]
    messages.append({"role": "user", "content": req.message})

    logger.info(f"[{session_id}] USER: {req.message}")

    result = enviar_mensaje(messages)
    raw_response = result["content"]

    # ── Guardrail: validar antes de enviar al usuario ─────────────────────
    validacion = validar_respuesta(raw_response, messages)
    if not validacion["ok"]:
        logger.warning(f"[{session_id}] GUARDRAIL bloqueó respuesta: {validacion['razon']}")
        raw_response = validacion["mensaje_alternativo"]

    messages.append({"role": "assistant", "content": raw_response})

    logger.info(f"[{session_id}] AGENT: {raw_response[:200]}")

    return ChatResponse(
        session_id=session_id,
        response=raw_response,
        timestamp=datetime.now().isoformat(),
    )


@app.post("/chat/reset")
def reset_session(req: ChatRequest) -> ChatResponse:
    """Reinicia la conversación de una sesión."""
    if req.session_id in sesiones:
        del sesiones[req.session_id]
    logger.info(f"Sesión reiniciada: {req.session_id}")
    return ChatResponse(
        session_id=req.session_id or str(uuid.uuid4()),
        response=WELCOME_MSG,
        timestamp=datetime.now().isoformat(),
    )


@app.get("/chat/{session_id}/history")
def get_history(session_id: str):
    """Devuelve el historial de una sesión."""
    if session_id not in sesiones:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return {"session_id": session_id, "messages": sesiones[session_id]}
