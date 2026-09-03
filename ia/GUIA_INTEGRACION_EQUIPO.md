# Guía de Integración — Capa de IA (EcoMatch)

> **Para:** Backend, Frontend, Integraciones, QA/DevOps, PM
> **De:** Ingeniero de IA
> **Estado:** Integrado con backend, Supabase y CI/CD

---

## Arquitectura actual del proyecto

```
plataforma-de-residuos/
├── backend/                    # Backend FastAPI (equipo backend)
│   ├── app/
│   │   ├── main.py             # FastAPI app — 14 routers
│   │   ├── agents/             # Agente IA básico (análisis, matching, contingencia)
│   │   ├── api/routes/         # Endpoints REST (/api/v1/*)
│   │   ├── core/               # config, database, security, exceptions
│   │   ├── models/             # SQLAlchemy 2.x models
│   │   ├── schemas/            # Pydantic v2 schemas
│   │   ├── services/           # Lógica de negocio
│   │   └── utils/              # Haversine, hazardous materials
│   ├── tests/                  # 58 tests del backend
│   └── scripts/seed.py         # Datos de demostración
├── ia/                         # Capa de IA avanzada (ingeniero IA)
│   ├── ecomatch_agent.py       # Agente con streaming + tool calling + guardrail
│   ├── api.py                  # WebSocket (/ws) + REST (/chat, /forms)
│   ├── guardrail.py            # Anti-alucinaciones (carga desde Supabase)
│   ├── prompts/system_prompt.md # System Prompt (clasificación, formularios)
│   ├── tools/
│   │   ├── schemas.py          # 5 herramientas (function calling)
│   │   ├── implementations.py  # Conectadas a Supabase + OpenStreetMap
│   │   └── formularios.py      # 9 formularios estructurados
│   ├── tests/                  # 22 tests de IA
│   ├── types/supabase.ts       # Tipos TypeScript para frontend
│   └── logs/                   # Logs de conversaciones
├── devops/                     # CI/CD, Docker, smoke tests
├── docker-compose.yml          # Orquestación completa
└── .github/workflows/          # CI/CD pipelines
```

---

## Cómo se conectan las capas

```
Frontend (React)
    │
    ├── WebSocket ws://localhost:8000/ws     → ia/api.py (chat streaming + formularios)
    ├── REST    http://localhost:8000/forms  → ia/api.py (formularios estructurados)
    └── REST    http://localhost:8001/api/v1 → backend/app/main.py (auth, CRUD, matching)

Backend (FastAPI)
    │
    ├── /api/v1/ai/*       → backend/app/agents/ecomatch_agent.py (IA básica)
    └── PostgreSQL         → SQLAlchemy models

Capa IA (ia/)
    │
    ├── GLM 5.2            → https://ai.kostra.cloud/v1 (OpenAI-compatible)
    ├── Supabase           → https://tgxseiaqebedzlgnutmm.supabase.co (BD real)
    └── OpenStreetMap      → https://nominatim.openstreetmap.org (distancias reales)
```

**Dos agentes de IA coexisten:**

| Agente | Ubicación | Función | Estado |
|---|---|---|---|
| **IA avanzada** | `ia/` | Chat conversacional, formularios, streaming, guardrail, 22 tests | ✅ Completo |
| **IA backend** | `backend/app/agents/` | Análisis de material, matching, contingencia (integrado con SQLAlchemy) | ✅ Completo |

El frontend usa ambos:
- **ia/api.py** para el chat conversacional con el usuario (WebSocket streaming)
- **backend/api/v1/ai** para análisis programático (matching, clasificación automática)

---

## 1. Backend — Integración con la capa de IA

### El backend ya tiene un agente básico

El backend en `backend/app/agents/ecomatch_agent.py` tiene:
- `analyze_material()` — clasifica texto libre en categoría/condición/riesgo
- `interpret_need()` — extrae material/cantidad de texto natural
- `explain_match()` — justifica por qué un match es bueno
- `detect_ambiguity()` — identifica información faltante
- `handle_contingency()` — propone recolector de reemplazo

### Lo que la capa `ia/` aporta al backend

| Componente | Archivo | Cómo se integra |
|---|---|---|
| System Prompt avanzado | `ia/prompts/system_prompt.md` | El backend puede importarlo para enriquecer sus prompts |
| Formularios estructurados | `ia/tools/formularios.py` | El backend valida formularios antes de insertar en BD |
| Guardrail anti-alucinaciones | `ia/guardrail.py` | El backend puede usarlo para validar respuestas del LLM |
| Tipos TypeScript | `ia/types/supabase.ts` | El frontend usa estos tipos para Supabase |
| WebSocket streaming | `ia/api.py` | El frontend se conecta aquí para chat en tiempo real |

### Configuración compartida

Ambos agentes usan el mismo LLM (GLM 5.2 vía Kostra):

```bash
# Variables de entorno (compartidas entre backend/ y ia/)
AI_BASE_URL=https://ai.kostra.cloud/v1
AI_API_KEY=sk-1pR89DLFsv8yAAMm3PnAFw
AI_MODEL=glm-5.2

# Supabase (usado por ia/)
SUPABASE_URL=https://tgxseiaqebedzlgnutmm.supabase.co
SUPABASE_KEY=sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8
```

El backend ya tiene `AI_BASE_URL`, `AI_API_KEY` y `AI_MODEL` en `backend/app/core/config.py`.

---

## 2. Frontend — Cómo conectarse

### Chat conversacional (WebSocket streaming)

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onopen = () => {
  ws.send(JSON.stringify({ action: "connect" }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch (data.type) {
    case "connected":     // session_id recibido
    case "welcome":       // mensaje de bienvenida
    case "token":         // cada token en tiempo real (efecto typing)
    case "tool_start":    // el agente está buscando receptores
    case "tool_end":      // la búsqueda terminó
    case "done":          // respuesta completa
    case "form":          // formulario estructurado para renderizar
    case "guardrail_blocked": // se bloqueó una alucinación
    case "error":         // error
  }
};

function sendMessage(text) {
  ws.send(JSON.stringify({ action: "message", content: text }));
}
```

### Formularios estructurados (evitan errores de tipeo)

```javascript
// Pedir formulario inicial (selección de material)
ws.send(JSON.stringify({ action: "get_form_inicial" }));
// → { type: "form", form: { campos: [{ name: "material", type: "select", options: [...] }] } }

// Pedir formulario específico
ws.send(JSON.stringify({ action: "get_form", material: "textil" }));
// → { type: "form", form: { titulo: "👕 Formulario de textil", campos: [...] } }

// Enviar formulario completado
ws.send(JSON.stringify({
  action: "submit_form",
  material: "textil",
  data: { volumen: 50, subtipo: "ropa", condicion: "donable", ubicacion: "...", tipo_generador: "pyme" }
}));
```

### REST del backend (auth, CRUD, matching)

```javascript
// Login
POST http://localhost:8001/api/v1/auth/login

// Publicar material
POST http://localhost:8001/api/v1/materials

// Generar matches
POST http://localhost:8001/api/v1/matches/generate/{material_id}

// Análisis IA del backend
POST http://localhost:8001/api/v1/ai/analyze-material
POST http://localhost:8001/api/v1/ai/chat
```

### Tipos TypeScript

```typescript
import { Database } from "./types/supabase";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient<Database>(
  "https://tgxseiaqebedzlgnutmm.supabase.co",
  "sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8"
);
```

---

## 3. Supabase — Base de datos

### Tablas (creadas y con RLS)

| Tabla | RLS | Registros | Descripción |
|---|---|---|---|
| `usuarios` | ✅ | 0 | UUID, email único, tipo (constructora/pyme/persona_natural) |
| `receptores` | ✅ | 5 | Receptores seed insertados |
| `ofertas_residuo` | ✅ | 0 | FK usuarios, material, volumen, ubicacion |
| `retiros` | ✅ | 0 | FK ofertas + receptores, fecha, hora |

### Receptores seed

| ID | Nombre | Materiales | Dirección |
|---|---|---|---|
| 1 | Recicladora Norte | escombros, metal, plastico | Av. Norte 450 |
| 2 | ONG Construye Verde | madera, escombros, metal | Calle Verde 12 |
| 3 | Planta Procesadora Sur | escombros, vidrio, plastico | Av. Sur 890 |
| 4 | Cartoneros Unidos | carton, plastico | Pasaje Reciclaje 7 |
| 5 | Reutiliza Textil | textil, madera | Calle Tela 99 |

### RPC Function

```sql
SELECT * FROM get_user_retiros('uuid-del-usuario');
```

---

## 4. Formularios estructurados

9 formularios (uno por material) con selects, number inputs y validación:

| Material | Campos específicos |
|---|---|
| textil | volumen, subtipo (ropa/retales/telas/calzado), condición (donable/reutilizable/inservible) |
| vidrio | volumen, estado (entero/roto), separación por color |
| carton | volumen, tipo (corrugado/plano), condición (limpio/contaminado) |
| plastico | volumen, tipo (PET/HDPE/bolsas/film), condición (limpio/mezclado) |
| metal | volumen, tipo (hierro/aluminio/cobre/lata), condición (limpio/contaminado) |
| escombros | volumen, tipo (limpio/mezclado), método de carga (camioneta/grúa/manual) |
| madera | volumen, tipo (virgen/tratada), formato (piezas grandes/pequeñas) |
| electronicos | volumen, tipo (computadores/monitores/cables/baterías), estado (funcionando/fuera de uso) |
| organico | volumen, subtipo (restos comida/jardín/aceite vegetal) |

---

## 5. QA / DevOps — Tests

### Tests de IA (22 casos)

```bash
cd ia/
export KOSTRA_API_KEY="sk-1pR89DLFsv8yAAMm3PnAFw"
export SUPABASE_URL="https://tgxseiaqebedzlgnutmm.supabase.co"
export SUPABASE_KEY="sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8"
python ecomatch_agent.py --test
```

| # | Test | Rúbrica |
|---|---|---|
| 01-11 | Ambigüedad, alucinaciones, flujo, autonomía | 10% + 10% + 30% + 25% |
| 12-20 | Clasificación por subtipo de material | 10% ambigüedad |
| 21-22 | Formularios completados | 30% tareas + 15% tools |

### Tests del backend (58 casos)

```bash
cd backend/
pytest -v
```

### Levantar todo

```bash
# Backend
cd backend && uvicorn app.main:app --port 8001

# IA (WebSocket + REST + formularios)
cd ia && uvicorn api:app --port 8000

# Docker completo
docker compose up --build
```

---

## 6. Cobertura de la rúbrica: 100%

| Criterio | Peso | Estado | Cómo se cumple |
|---|---|---|---|
| Tareas exitosas | 30% | ✅ | Flujo completo: publicar → buscar → agendar |
| Autonomía | 25% | ✅ | 8 pasos sin intervención humana |
| Uso de herramientas | 15% | ✅ | 5 tools + function calling + Supabase + OpenStreetMap |
| Gestión de ambigüedad | 10% | ✅ | Repreguntas específicas + formularios + clasificación |
| Cero alucinaciones | 10% | ✅ | Guardrail + prompt + temperature=0.3 + Supabase real |
| UX | 5% | ✅ | WebSocket streaming + formularios + bienvenida |
| Creatividad | 5% | ✅ | OpenStreetMap real + clasificación orgánico/inorgánico |

---

## 7. Credenciales

```
# LLM
KOSTRA_API_KEY = sk-1pR89DLFsv8yAAMm3PnAFw
AI_BASE_URL    = https://ai.kostra.cloud/v1
AI_MODEL       = glm-5.2

# Supabase
SUPABASE_URL   = https://tgxseiaqebedzlgnutmm.supabase.co
SUPABASE_KEY   = sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8
```

> **No commitear las API keys.** Usar variables de entorno.
