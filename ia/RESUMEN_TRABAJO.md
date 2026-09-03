# Resumen de Trabajo — Capa de IA (EcoMatch)

> **Rol:** Ingeniero de IA
> **Proyecto:** Plataforma EcoMatch / ReVínculo — Economía circular
> **Modelo:** GLM 5.2 vía Kostra (OpenAI-compatible)
> **Fecha:** Septiembre 2026
> **Estado:** ✅ Integrado con backend, Supabase y CI/CD

---

## 1. System Prompt

**Archivo:** `ia/prompts/system_prompt.md`

- Identidad: EcoMatch, agente de orquestación logística para economía circular
- Cero alucinaciones: prohibición de inventar empresas, direcciones, teléfonos o leyes
- Clasificación de residuos: orgánico / inorgánico con 9 subtipos
- Gestión de ambigüedad: preguntas específicas por tipo de material
- Formularios estructurados: inserción de datos via formularios, no chat libre
- Flujo obligatorio de 8 pasos
- Restricciones de dominio: declina preguntas fuera de gestión de residuos

---

## 2. Function Calling — 5 Herramientas

| Herramienta | Conexión |
|---|---|
| `buscar_receptores` | ✅ Supabase real |
| `crear_oferta_residuo` | ✅ Supabase real |
| `agendar_retiro` | ✅ Supabase real |
| `calcular_distancia` | ✅ OpenStreetMap Nominatim (gratis) |
| `obtener_historial_usuario` | ✅ Supabase real (RPC function) |

---

## 3. Base de Datos — Supabase

**Proyecto:** `tgxseiaqebedzlgnutmm`

### Tablas creadas con RLS

| Tabla | RLS | Registros |
|---|---|---|
| `usuarios` | ✅ | 0 |
| `receptores` | ✅ | 5 (seed) |
| `ofertas_residuo` | ✅ | 0 |
| `retiros` | ✅ | 0 |

- 13 RLS policies
- RPC function `get_user_retiros` con `SECURITY INVOKER`
- 0 warnings de seguridad

---

## 4. Guardrail Anti-Alucinaciones

**Archivo:** `ia/guardrail.py`

- Bloquea leyes/decretos inventados
- Valida receptores contra Supabase (carga dinámica)
- Bloquea respuestas >3000 chars
- Bloquea teléfonos de receptores no válidos

---

## 5. Formularios Estructurados

**Archivo:** `ia/tools/formularios.py`

9 formularios (textil, vidrio, carton, plastico, metal, escombros, madera, electronicos, organico) + formulario inicial de selección.

Ventajas: cero errores de tipeo, menos tokens, mejor UX, menos carga en BD.

---

## 6. API — WebSocket + REST

**Archivo:** `ia/api.py`

### WebSocket `/ws` (streaming token a token)

| Acción cliente | Descripción |
|---|---|
| `connect` | Iniciar conexión |
| `message` | Chat libre |
| `get_form_inicial` | Pedir selección de material |
| `get_form` | Pedir formulario por material |
| `submit_form` | Enviar formulario completado |
| `reset` | Reiniciar conversación |

| Evento servidor | Descripción |
|---|---|
| `token` | Cada token en tiempo real |
| `tool_start/end` | Tool en ejecución |
| `done` | Respuesta completa |
| `form` | Formulario para renderizar |
| `guardrail_blocked` | Alucinación bloqueada |

### REST

| Endpoint | Descripción |
|---|---|
| `POST /chat` | Chat sin streaming |
| `GET /forms` | Formulario inicial |
| `GET /forms/{material}` | Formulario por material |
| `POST /forms/submit` | Enviar formulario |
| `GET /health` | Health check |

---

## 7. Integración con el Backend

El proyecto tiene **dos agentes de IA** que coexisten:

| Agente | Ubicación | Función |
|---|---|---|
| **IA avanzada** | `ia/` | Chat conversacional, streaming, formularios, guardrail |
| **IA backend** | `backend/app/agents/` | Análisis de material, matching, contingencia |

**El frontend usa ambos:**
- `ia/api.py` (puerto 8000) → chat conversacional con WebSocket
- `backend/` (puerto 8001) → auth, CRUD, matching, análisis programático

**Ambos usan el mismo LLM:** GLM 5.2 vía Kostra.

---

## 8. Tests — 22 casos

| Grupo | Tests | Rúbrica |
|---|---|---|
| Originales (01-11) | Ambigüedad, alucinaciones, flujo, autonomía | 30% + 25% + 10% + 10% |
| Clasificación (12-20) | Por subtipo: textil, vidrio, carton, plastico, madera, electronicos, organico, metal | 10% ambigüedad |
| Formularios (21-22) | Datos estructurados → busca receptores | 30% tareas + 15% tools |

---

## 9. Cobertura de la Rúbrica: 100%

| Criterio | Peso | Estado |
|---|---|---|
| Tareas exitosas | 30% | ✅ |
| Autonomía | 25% | ✅ |
| Uso de herramientas | 15% | ✅ |
| Gestión de ambigüedad | 10% | ✅ |
| Cero alucinaciones | 10% | ✅ |
| UX | 5% | ✅ |
| Creatividad | 5% | ✅ |

---

## 10. Estructura final

```
ia/
├── ecomatch_agent.py           # Agente (chat + streaming + tools + guardrail)
├── api.py                      # WebSocket + REST + formularios
├── guardrail.py                # Anti-alucinaciones
├── prompts/system_prompt.md    # System Prompt
├── tools/
│   ├── schemas.py              # 5 herramientas (function calling)
│   ├── implementations.py      # Supabase + OpenStreetMap
│   └── formularios.py          # 9 formularios estructurados
├── tests/                      # 22 casos de prueba
├── types/supabase.ts           # Tipos TypeScript
├── logs/                       # Logs de conversaciones
├── GUIA_INTEGRACION_EQUIPO.md  # Guía para el equipo
├── RESUMEN_TRABAJO.md          # Este documento
└── README.md                   # Setup y uso
```

---

## 11. Configuración

```bash
# LLM
KOSTRA_API_KEY="sk-1pR89DLFsv8yAAMm3PnAFw"

# Supabase
SUPABASE_URL="https://tgxseiaqebedzlgnutmm.supabase.co"
SUPABASE_KEY="sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8"
```

```bash
# Instalar
cd ia/ && pip install -r requirements.txt

# Chat interactivo
python ecomatch_agent.py

# Tests
python ecomatch_agent.py --test

# API (WebSocket + REST)
uvicorn api:app --port 8000
```
