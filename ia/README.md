# Capa de IA — EcoMatch

> **Estado:** Unificada con el backend.
> El agente de IA ahora vive en `backend/app/agents/`.

## Qué hay aquí

Los tests (22 casos) y el system prompt de referencia. El código del agente
se movió al backend para que tenga acceso a SQLAlchemy (BD real).

## Arquitectura unificada

```
Frontend
    │
    └── WebSocket ws://localhost:8001/api/v1/ai/ws  →  backend/app/agents/ecomatch_agent.py
                                                         ├── prompts.py      (system prompt + clasificación)
                                                         ├── guardrail.py    (anti-alucinaciones)
                                                         ├── formularios.py  (9 formularios estructurados)
                                                         ├── tools.py        (function calling → SQLAlchemy)
                                                         └── llm_client.py   (GLM 5.2 vía Kostra)
```

## Tests

```bash
cd ia/
export KOSTRA_API_KEY="sk-1pR89DLFsv8yAAMm3PnAFw"
python ecomatch_agent.py --test
```

## Documentación

" en `GUIA_INTEGRACION_EQUIPO.md` y `RESUMEN_TRABAJO.md`.
