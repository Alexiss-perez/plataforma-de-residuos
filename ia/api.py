"""
API del Agente EcoMatch — FastAPI + WebSocket
==============================================
Expone el agente de IA para que el Frontend se conecte via WebSocket (streaming)
o via REST (sin streaming).

Endpoints:
    WS   /ws               — WebSocket streaming (token a token)
    POST /chat             — REST sin streaming
    POST /chat/reset       — reinicia la conversación
    GET  /health           — health check

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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ── Imports del agente ──────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from ecomatch_agent import enviar_mensaje, enviar_mensaje_stream, SYSTEM_PROMPT
from guardrail import validar_respuesta
from tools.formularios import obtener_formulario, obtener_formulario_inicial, validar_formulario

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
    timestamp: str


# ── Helper: obtener o crear sesión ─────────────────────────────────────────
def get_or_create_session(session_id: str | None) -> str:
    sid = session_id or str(uuid.uuid4())
    if sid not in sesiones:
        sesiones[sid] = [{"role": "system", "content": SYSTEM_PROMPT}]
        logger.info(f"Nueva sesión: {sid}")
    return sid


# ── Health ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "model": "glm-5.2", "timestamp": datetime.now().isoformat()}


# ════════════════════════════════════════════════════════════════════════════
#  WEBSOCKET — Streaming token a token
# ════════════════════════════════════════════════════════════════════════════
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    WebSocket para chat streaming.

    Cliente envía:
        {"action": "connect"}                          — iniciar conexión
        {"action": "message", "content": "texto"}      — enviar mensaje
        {"action": "reset"}                            — reiniciar conversación

    Servidor responde:
        {"type": "connected", "session_id": "..."}
        {"type": "welcome", "content": "..."}
        {"type": "token", "content": "..."}            — cada token en tiempo real
        {"type": "tool_start", "name": "...", "args": {...}}
        {"type": "tool_end", "name": "...", "result": "..."}
        {"type": "done", "content": "..."}             — respuesta completa
        {"type": "guardrail_blocked", "razon": "..."}
        {"type": "error", "message": "..."}
    """
    await ws.accept()

    session_id = None

    try:
        while True:
            data = await ws.receive_json()
            action = data.get("action")

            # ── Connect ───────────────────────────────────────────────
            if action == "connect":
                session_id = get_or_create_session(data.get("session_id"))
                await ws.send_json({
                    "type": "connected",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                })
                await ws.send_json({"type": "welcome", "content": WELCOME_MSG})
                continue

            # ── Reset ─────────────────────────────────────────────────
            if action == "reset":
                if session_id and session_id in sesiones:
                    del sesiones[session_id]
                session_id = get_or_create_session(session_id)
                await ws.send_json({"type": "welcome", "content": WELCOME_MSG})
                continue

            # ── Message ───────────────────────────────────────────────
            if action == "message":
                if not session_id:
                    session_id = get_or_create_session(None)
                    await ws.send_json({"type": "connected", "session_id": session_id})

                content = data.get("content", "").strip()
                if not content:
                    continue

                # Atajo de bienvenida
                if content.lower() in ("hola", "hi", "hello", "inicio"):
                    await ws.send_json({"type": "welcome", "content": WELCOME_MSG})
                    continue

                messages = sesiones[session_id]
                messages.append({"role": "user", "content": content})
                logger.info(f"[{session_id}] USER: {content}")

                # ── Streaming token a token ──────────────────────────
                final_content = ""
                try:
                    for evento in enviar_mensaje_stream(messages):
                        await ws.send_json(evento)
                        if evento["type"] == "done":
                            final_content = evento["content"]
                except Exception as e:
                    logger.error(f"[{session_id}] Stream error: {e}")
                    await ws.send_json({"type": "error", "message": str(e)})
                    continue

                messages.append({"role": "assistant", "content": final_content})
                logger.info(f"[{session_id}] AGENT: {final_content[:200]}")
                continue

            # ── Obtener formulario inicial (selección de material) ────
            if action == "get_form_inicial":
                form = obtener_formulario_inicial()
                await ws.send_json({"type": "form", "form": form})
                continue

            # ── Obtener formulario por material ───────────────────────
            if action == "get_form":
                material = data.get("material", "")
                form = obtener_formulario(material)
                if form:
                    await ws.send_json({"type": "form", "form": form})
                else:
                    await ws.send_json({"type": "error", "message": f"No hay formulario para '{material}'"})
                continue

            # ── Enviar formulario completado ──────────────────────────
            if action == "submit_form":
                if not session_id:
                    session_id = get_or_create_session(None)
                    await ws.send_json({"type": "connected", "session_id": session_id})

                material = data.get("material", "")
                form_data = data.get("data", {})

                # Validar formulario
                validacion = validar_formulario(material, form_data)
                if not validacion["ok"]:
                    await ws.send_json({
                        "type": "form_validation_error",
                        "errors": validacion["errors"],
                    })
                    continue

                datos = validacion["data"]
                logger.info(f"[{session_id}] FORM SUBMIT: {material} -> {datos}")

                # Construir mensaje estructurado para el agente
                volumen_str = f"{datos.get('volumen', '')} kg"
                ubicacion = datos.get("ubicacion", "")
                tipo_generador = datos.get("tipo_generador", "")

                # Notas con los campos extra del formulario
                notas_parts = []
                for key, val in datos.items():
                    if key not in ("volumen", "ubicacion", "tipo_generador"):
                        notas_parts.append(f"{key}: {val}")
                notas = ", ".join(notas_parts)

                # Enviar al agente como mensaje estructurado
                msg_estructurado = (
                    f"[FORMULARIO COMPLETADO] Material: {material}, "
                    f"Volumen: {volumen_str}, Ubicación: {ubicacion}, "
                    f"Tipo generador: {tipo_generador}, Notas: {notas}"
                )

                messages = sesiones[session_id]
                messages.append({"role": "user", "content": msg_estructurado})

                # Streaming de la respuesta
                final_content = ""
                try:
                    for evento in enviar_mensaje_stream(messages):
                        await ws.send_json(evento)
                        if evento["type"] == "done":
                            final_content = evento["content"]
                except Exception as e:
                    logger.error(f"[{session_id}] Stream error: {e}")
                    await ws.send_json({"type": "error", "message": str(e)})
                    continue

                messages.append({"role": "assistant", "content": final_content})
                logger.info(f"[{session_id}] AGENT: {final_content[:200]}")
                continue

            await ws.send_json({"type": "error", "message": f"Acción desconocida: {action}"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket desconectado: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════════════
#  REST — Sin streaming (compatibilidad)
# ════════════════════════════════════════════════════════════════════════════
@app.post("/chat")
def chat(req: ChatRequest) -> ChatResponse:
    """Endpoint REST: envía un mensaje y devuelve la respuesta completa."""
    session_id = get_or_create_session(req.session_id)

    if req.message.lower().strip() in ("hola", "hi", "hello", "inicio"):
        return ChatResponse(session_id=session_id, response=WELCOME_MSG, timestamp=datetime.now().isoformat())

    messages = sesiones[session_id]
    messages.append({"role": "user", "content": req.message})
    logger.info(f"[{session_id}] USER: {req.message}")

    result = enviar_mensaje(messages)
    raw_response = result["content"]

    validacion = validar_respuesta(raw_response, messages)
    if not validacion["ok"]:
        logger.warning(f"[{session_id}] GUARDRAIL bloqueó: {validacion['razon']}")
        raw_response = validacion["mensaje_alternativo"]

    messages.append({"role": "assistant", "content": raw_response})
    logger.info(f"[{session_id}] AGENT: {raw_response[:200]}")

    return ChatResponse(session_id=session_id, response=raw_response, timestamp=datetime.now().isoformat())


@app.post("/chat/reset")
def reset_session(req: ChatRequest) -> ChatResponse:
    """Reinicia la conversación."""
    if req.session_id in sesiones:
        del sesiones[req.session_id]
    logger.info(f"Sesión reiniciada: {req.session_id}")
    return ChatResponse(session_id=req.session_id or str(uuid.uuid4()), response=WELCOME_MSG, timestamp=datetime.now().isoformat())


@app.get("/chat/{session_id}/history")
def get_history(session_id: str):
    """Devuelve el historial de una sesión."""
    if session_id not in sesiones:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return {"session_id": session_id, "messages": sesiones[session_id]}


# ════════════════════════════════════════════════════════════════════════════
#  REST — Formularios
# ════════════════════════════════════════════════════════════════════════════
@app.get("/forms")
def get_form_inicial():
    """Devuelve el formulario inicial de selección de material."""
    return obtener_formulario_inicial()


@app.get("/forms/{material}")
def get_form_material(material: str):
    """Devuelve el formulario estructurado para un tipo de material."""
    form = obtener_formulario(material)
    if not form:
        raise HTTPException(status_code=404, detail=f"No hay formulario para '{material}'")
    return form


class FormSubmitRequest(BaseModel):
    session_id: str | None = None
    material: str
    data: dict


@app.post("/forms/submit")
def submit_form(req: FormSubmitRequest):
    """Recibe un formulario completado, lo valida y lo envía al agente."""
    validacion = validar_formulario(req.material, req.data)
    if not validacion["ok"]:
        return {"ok": False, "errors": validacion["errors"]}

    session_id = get_or_create_session(req.session_id)
    datos = validacion["data"]

    volumen_str = f"{datos.get('volumen', '')} kg"
    ubicacion = datos.get("ubicacion", "")
    tipo_generador = datos.get("tipo_generador", "")

    notas_parts = []
    for key, val in datos.items():
        if key not in ("volumen", "ubicacion", "tipo_generador"):
            notas_parts.append(f"{key}: {val}")
    notas = ", ".join(notas_parts)

    msg_estructurado = (
        f"[FORMULARIO COMPLETADO] Material: {req.material}, "
        f"Volumen: {volumen_str}, Ubicación: {ubicacion}, "
        f"Tipo generador: {tipo_generador}, Notas: {notas}"
    )

    messages = sesiones[session_id]
    messages.append({"role": "user", "content": msg_estructurado})
    logger.info(f"[{session_id}] FORM SUBMIT: {req.material} -> {datos}")

    result = enviar_mensaje(messages)
    raw_response = result["content"]

    validacion_resp = validar_respuesta(raw_response, messages)
    if not validacion_resp["ok"]:
        raw_response = validacion_resp["mensaje_alternativo"]

    messages.append({"role": "assistant", "content": raw_response})

    return {
        "ok": True,
        "session_id": session_id,
        "response": raw_response,
        "timestamp": datetime.now().isoformat(),
    }
