from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.agents.ecomatch_agent import EcoMatchAgent
from app.agents.formularios import obtener_formulario, obtener_formulario_inicial, validar_formulario
from app.agents.prompts import CHAT_SYSTEM_PROMPT
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

# Sesiones de chat en memoria (en producción: Redis)
sesiones: dict[str, list] = {}

WELCOME_MSG = (
    "👋 ¡Hola! Soy **EcoMatch**, tu agente de economía circular. ♻️\n\n"
    "Puedo ayudarte a:\n"
    "1. **Publicar residuos** que quieres que retiren de tu ubicación\n"
    "2. **Buscar receptores** cerca de ti (ONGs, plantas de reciclaje, pymes)\n"
    "3. **Coordinar el retiro** entre tú y el receptor\n\n"
    "Cuéntame: ¿qué residuo tienes y dónde estás ubicado?"
)


# ── Endpoints REST programáticos ────────────────────────────────────────────
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


# ── Endpoints REST de formularios ──────────────────────────────────────────
@router.get("/forms")
def get_form_inicial():
    return obtener_formulario_inicial()


@router.get("/forms/{material}")
def get_form_material(material: str):
    form = obtener_formulario(material)
    if not form:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"No hay formulario para '{material}'")
    return form


@router.post("/forms/submit")
def submit_form(req: AIChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import json
    data = req.context or {}
    material = data.get("material", "")
    form_data = data.get("data", {})

    validacion = validar_formulario(material, form_data)
    if not validacion["ok"]:
        return {"ok": False, "errors": validacion["errors"]}

    datos = validacion["data"]
    msg_estructurado = f"[FORMULARIO COMPLETADO] Material: {material}, Datos: {json.dumps(datos)}"
    result = EcoMatchAgent(db).chat(msg_estructurado)
    return {"ok": True, "response": result["response"]}


# ── WebSocket streaming ────────────────────────────────────────────────────
@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    WebSocket para chat streaming + formularios.

    Acciones del cliente:
        {"action": "connect"}                     — iniciar conexión
        {"action": "message", "content": "..."}   — enviar mensaje
        {"action": "get_form_inicial"}            — pedir selección de material
        {"action": "get_form", "material": "..."} — pedir formulario por material
        {"action": "submit_form", "material": "...", "data": {...}}
        {"action": "reset"}                       — reiniciar conversación

    Eventos del servidor:
        {"type": "connected", "session_id": "..."}
        {"type": "welcome", "content": "..."}
        {"type": "token", "content": "..."}       — cada token en tiempo real
        {"type": "done", "content": "..."}        — respuesta completa
        {"type": "form", "form": {...}}           — formulario para renderizar
        {"type": "form_validation_error", "errors": [...]}
        {"type": "guardrail_blocked", "razon": "..."}
        {"type": "error", "message": "..."}
    """
    await ws.accept()
    session_id = None

    try:
        while True:
            data = await ws.receive_json()
            action = data.get("action")

            if action == "connect":
                session_id = str(uuid.uuid4())
                sesiones[session_id] = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
                await ws.send_json({"type": "connected", "session_id": session_id})
                await ws.send_json({"type": "welcome", "content": WELCOME_MSG})
                continue

            if action == "reset":
                if session_id and session_id in sesiones:
                    del sesiones[session_id]
                session_id = str(uuid.uuid4())
                sesiones[session_id] = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
                await ws.send_json({"type": "welcome", "content": WELCOME_MSG})
                continue

            if action == "get_form_inicial":
                await ws.send_json({"type": "form", "form": obtener_formulario_inicial()})
                continue

            if action == "get_form":
                material = data.get("material", "")
                form = obtener_formulario(material)
                if form:
                    await ws.send_json({"type": "form", "form": form})
                else:
                    await ws.send_json({"type": "error", "message": f"No hay formulario para '{material}'"})
                continue

            if action == "submit_form":
                import json
                material = data.get("material", "")
                form_data = data.get("data", {})
                validacion = validar_formulario(material, form_data)
                if not validacion["ok"]:
                    await ws.send_json({"type": "form_validation_error", "errors": validacion["errors"]})
                    continue

                datos = validacion["data"]
                msg = f"[FORMULARIO COMPLETADO] Material: {material}, Datos: {json.dumps(datos)}"

                # Usar el agente del backend con la DB
                db = next(get_db())
                try:
                    agente = EcoMatchAgent(db)
                    for evento in agente.chat_stream(msg):
                        await ws.send_json(evento)
                finally:
                    db.close()
                continue

            if action == "message":
                if not session_id:
                    session_id = str(uuid.uuid4())
                    sesiones[session_id] = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
                    await ws.send_json({"type": "connected", "session_id": session_id})

                content = data.get("content", "").strip()
                if not content:
                    continue

                if content.lower() in ("hola", "hi", "hello", "inicio"):
                    await ws.send_json({"type": "welcome", "content": WELCOME_MSG})
                    continue

                # Usar el agente del backend con la DB
                db = next(get_db())
                try:
                    agente = EcoMatchAgent(db)
                    for evento in agente.chat_stream(content):
                        await ws.send_json(evento)
                finally:
                    db.close()
                continue

            await ws.send_json({"type": "error", "message": f"Acción desconocida: {action}"})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
