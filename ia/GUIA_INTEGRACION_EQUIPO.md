# Guía de Integración — Capa de IA (EcoMatch)

> **Para:** Backend, Frontend, Integraciones, QA/DevOps, PM
> **De:** Ingeniero de IA
> **Estado:** Listo para integrar

---

## ¿Qué está hecho?

La capa de IA está **100% funcional** y conectada a **Supabase** (PostgreSQL real).
El agente funciona con GLM 5.2 vía la API de Kostra, tiene 5 herramientas (function calling),
guardrail anti-alucinaciones, **WebSocket streaming** + API REST, y 11 tests que pasan.

```
ia/
├── ecomatch_agent.py       # Agente principal (chat + streaming + tool calling + guardrail)
├── api.py                  # API FastAPI — WebSocket (/ws) + REST (/chat)
├── guardrail.py            # Capa anti-alucinaciones (carga receptores desde Supabase)
├── prompts/
│   └── system_prompt.md    # System Prompt (identidad, reglas, flujo)
├── tools/
│   ├── schemas.py          # Esquemas JSON de las 5 herramientas
│   ├── implementations.py  # Implementaciones conectadas a Supabase + OpenStreetMap real
│   └── __init__.py
├── tests/                  # 11 casos de prueba
├── types/
│   └── supabase.ts         # Tipos TypeScript generados para el frontend
├── logs/                   # Logs de conversaciones (se generan automáticamente)
├── requirements.txt
└── README.md
```

---

## 0. Configuración — Variables de entorno

```bash
# LLM (GLM 5.2 via Kostra)
export KOSTRA_API_KEY="sk-1pR89DLFsv8yAAMm3PnAFw"

# Supabase (BD real)
export SUPABASE_URL="https://tgxseiaqebedzlgnutmm.supabase.co"
export SUPABASE_KEY="sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8"
```

---

## 1. Backend — Base de datos en Supabase

### Estado actual: LISTO

Las tablas ya están creadas en Supabase con RLS policies y datos seed:

| Tabla | RLS | Registros | Descripción |
|---|---|---|---|
| `usuarios` | ✅ | 0 | UUID PK, email único, tipo (constructora/pyme/persona_natural) |
| `receptores` | ✅ | 5 | Receptores seed insertados |
| `ofertas_residuo` | ✅ | 0 | FK a usuarios, índices en material/usuario/estado |
| `retiros` | ✅ | 0 | FK a ofertas + receptores, índices en oferta/receptor/estado |

### Esquema

```sql
-- usuarios
CREATE TABLE usuarios (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      VARCHAR(255) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    tipo        VARCHAR(50) CHECK (tipo IN ('constructora', 'pyme', 'persona_natural')),
    direccion   TEXT,
    telefono    VARCHAR(50),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- receptores
CREATE TABLE receptores (
    id                    SERIAL PRIMARY KEY,
    nombre                VARCHAR(255) NOT NULL,
    tipo                  VARCHAR(50) CHECK (tipo IN ('planta_reciclaje', 'ong', 'pyme')),
    materiales_aceptados  TEXT[] NOT NULL DEFAULT '{}',
    direccion             TEXT NOT NULL,
    telefono              VARCHAR(50),
    capacidad_disponible  VARCHAR(100),
    lat                   DOUBLE PRECISION,
    lon                   DOUBLE PRECISION,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);

-- ofertas_residuo
CREATE TABLE ofertas_residuo (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id      UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    material        VARCHAR(50) NOT NULL,
    volumen         VARCHAR(100) NOT NULL,
    ubicacion       TEXT NOT NULL,
    tipo_generador  VARCHAR(50) NOT NULL,
    notas           TEXT,
    estado          VARCHAR(20) NOT NULL DEFAULT 'publicada',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- retiros
CREATE TABLE retiros (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    oferta_id   UUID NOT NULL REFERENCES ofertas_residuo(id) ON DELETE CASCADE,
    receptor_id INTEGER NOT NULL REFERENCES receptores(id) ON DELETE CASCADE,
    fecha       DATE NOT NULL,
    hora        TIME NOT NULL,
    estado      VARCHAR(20) NOT NULL DEFAULT 'agendado',
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### RLS Policies

- **usuarios:** cada usuario ve/edita solo su propio perfil
- **receptores:** lectura pública (cualquiera puede ver), escritura solo constructoras
- **ofertas_residuo:** cada usuario ve/edita solo sus propias ofertas
- **retiros:** cada usuario ve/edita retiros de sus propias ofertas

### Función RPC

```sql
-- Obtener retiros de un usuario con join a receptores y ofertas
SELECT * FROM get_user_retiros('uuid-del-usuario');
```

### Receptores seed (ya insertados)

| ID | Nombre | Materiales | Dirección |
|---|---|---|---|
| 1 | Recicladora Norte | escombros, metal, plastico | Av. Norte 450 |
| 2 | ONG Construye Verde | madera, escombros, metal | Calle Verde 12 |
| 3 | Planta Procesadora Sur | escombros, vidrio, plastico | Av. Sur 890 |
| 4 | Cartoneros Unidos | carton, plastico | Pasaje Reciclaje 7 |
| 5 | Reutiliza Textil | textil, madera | Calle Tela 99 |

Materiales válidos: `escombros, madera, plastico, carton, metal, vidrio, organico, electronicos, textil`

### Lo que el Backend debe hacer

Las herramientas en `ia/tools/implementations.py` **ya están conectadas a Supabase**.
El único pendiente es que el `usuario_id` en `crear_oferta_residuo_impl` debe venir del JWT del frontend:

```python
# En implementations.py, línea ~60
# TODO: el usuario_id debe venir del JWT del frontend.
usuario_id = os.environ.get("ECOMATCH_USER_ID", None)
```

El Backend debe pasar el `usuario_id` desde el token de autenticación de Supabase Auth.

---

## 2. Frontend — Cómo conectarse al agente

### Opción A: WebSocket Streaming (RECOMENDADO)

Levanta la API del agente:

```bash
cd ia/
uvicorn api:app --port 8000
```

Conexión WebSocket:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");

let sessionId = null;

ws.onopen = () => {
  // Iniciar conexión
  ws.send(JSON.stringify({ action: "connect" }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case "connected":
      sessionId = data.session_id;
      break;

    case "welcome":
      // Mostrar mensaje de bienvenida en el chat
      displayMessage(data.content);
      break;

    case "token":
      // CADA TOKEN EN TIEMPO REAL — appendar al mensaje en construcción
      // Esto da el efecto de "escribiendo en tiempo real"
      appendToken(data.content);
      break;

    case "tool_start":
      // El agente está llamando una herramienta
      // Ej: mostrar "Buscando receptores..." en la UI
      showStatus(`Buscando ${data.name}...`);
      break;

    case "tool_end":
      // La herramienta terminó
      showStatus("");
      break;

    case "done":
      // Respuesta completa recibida
      finalizeMessage(data.content);
      break;

    case "guardrail_blocked":
      // El guardrail bloqueó una posible alucinación
      console.warn("Bloqueado:", data.razon);
      break;

    case "error":
      console.error("Error:", data.message);
      break;
  }
};

// Enviar mensaje al agente
function sendMessage(text) {
  ws.send(JSON.stringify({ action: "message", content: text }));
}

// Reiniciar conversación
function resetChat() {
  ws.send(JSON.stringify({ action: "reset" }));
}
```

### Opción B: REST (sin streaming)

```javascript
// Enviar mensaje
POST http://localhost:8000/chat
{ "session_id": sessionId, "message": "Tengo 15 m3 de escombros..." }

// Response
{ "session_id": "...", "response": "¡Tu oferta fue registrada!...", "timestamp": "..." }

// Reiniciar
POST http://localhost:8000/chat/reset
{ "session_id": sessionId }

// Historial
GET http://localhost:8000/chat/{session_id}/history

// Health check
GET http://localhost:8000/health
```

### Tipos TypeScript

Los tipos de Supabase están en `ia/types/supabase.ts`. Para usarlos en el frontend:

```typescript
import { Database } from "./types/supabase";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient<Database>(
  "https://tgxseiaqebedzlgnutmm.supabase.co",
  "sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8"
);

// Ejemplo: obtener receptores
const { data } = await supabase.from("receptores").select("*");
```

### Manejo de estados en el frontend

| Estado | Cuándo | UX sugerida |
|---|---|---|
| `connected` | WebSocket conectado | Habilitar input |
| `welcome` | Mensaje de bienvenida | Mostrar en chat |
| `token` | Cada token recibido | Appendar al mensaje (efecto typing) |
| `tool_start` | Agente usando herramienta | "Buscando receptores..." |
| `tool_end` | Herramienta terminó | Quitar status |
| `done` | Respuesta completa | Finalizar mensaje |
| `error` | WebSocket caído | "El agente no está disponible" |

---

## 3. Ingeniero de Integraciones — APIs externas

### Ya integrado: OpenStreetMap Nominatim (gratis)

La función `calcular_distancia` ya usa la API real de OpenStreetMap:
- **No requiere API key**
- **Endpoint:** `https://nominatim.openstreetmap.org/search`
- **Límite:** 1 request/segundo (política de uso justo)
- **User-Agent:** `EcoMatch/1.0` (ya configurado)

Si necesitas más precisión o geocodificación inversa, considera:
- **Mapbox** (gratis hasta 100k requests/mes) — mejor para producción
- **Google Maps** ($2 per 1000 requests) — mejor para routing detallado

Para cambiar la API de mapas, edita `calcular_distancia_impl` en `ia/tools/implementations.py`.

### Pendiente: SendGrid / Email de confirmación

Cuando se agende un retiro, el backend debería enviar un email de confirmación.
El agente ya devuelve los datos del retiro agendado:

```json
{
  "status": "ok",
  "retiro_id": "uuid",
  "detalle": {
    "receptor": "Recicladora Norte",
    "material": "escombros",
    "volumen": "20 m3",
    "origen": "Av. Principal 123",
    "destino": "Av. Norte 450",
    "fecha": "2025-12-15",
    "hora": "10:00"
  }
}
```

Usa esos datos para llenar la plantilla de email.

---

## 4. QA / DevOps — Tests y CI/CD

### Ejecutar los 11 tests

```bash
cd ia/
export KOSTRA_API_KEY="sk-1pR89DLFsv8yAAMm3PnAFw"
export SUPABASE_URL="https://tgxseiaqebedzlgnutmm.supabase.co"
export SUPABASE_KEY="sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8"
python ecomatch_agent.py --test
```

### Levantar la API

```bash
cd ia/
uvicorn api:app --port 8000
# WebSocket: ws://localhost:8000/ws
# REST:      http://localhost:8000/chat
# Docs:      http://localhost:8000/docs
```

### Catálogo de tests

| # | Test | Qué valida | Rúbrica |
|---|---|---|---|
| 01 | Ambigüedad — volumen faltante | Repregunta antes de buscar | 10% ambigüedad |
| 02 | Ambigüedad — tipo de madera | Repregunta tipo y cantidad | 10% ambigüedad |
| 03 | Flujo completo | Registra + busca + presenta | 30% tareas |
| 04 | Cero alucinaciones | Se niega a inventar receptores | 10% fiabilidad |
| 05 | Fuera de dominio | Redirige a residuos | 25% autonomía |
| 06 | Lenguaje informal | Interpreta "cartones" = cartón | 10% ambigüedad |
| 07 | Info contradictoria | Detecta 500kg ≠ 3 toneladas | 10% ambigüedad |
| 08 | No hay receptores | Informa, no inventa | 10% fiabilidad |
| 09 | Multi-turn | Repregunta → completa → busca | 25% autonomía |
| 10 | Ley/regulación | No inventa leyes | 10% fiabilidad |
| 11 | E2E agendar retiro | Flujo completo hasta agendar | 30% tareas |

### Crear nuevos tests

Crea un archivo JSON en `ia/tests/`:

```json
{
  "nombre": "test_12_mi_caso",
  "descripcion": "Descripción de qué valida",
  "resultado_esperado": "Qué debe hacer el agente",
  "pasos": [
    {"user": "primer mensaje del usuario"},
    {"user": "segundo mensaje (si es multi-turn)"}
  ]
}
```

Se ejecutará automáticamente con `--test`.

### Logs

Los logs se guardan en `ia/logs/agent.log`. Cada interacción registra:
- Nueva sesión creada
- Mensaje del usuario
- Tools invocadas (con argumentos y resultados)
- Respuesta del agente
- Bloqueos del guardrail (si los hay)

### CI/CD sugerido

```yaml
# .github/workflows/ai-tests.yml
name: AI Agent Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r ia/requirements.txt
      - run: cd ia && python ecomatch_agent.py --test
        env:
          KOSTRA_API_KEY: ${{ secrets.KOSTRA_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
```

---

## 5. PM / Product Owner — Estado del apartado de IA

### Cobertura de la rúbrica

| Criterio | Peso | Estado | Cómo se cumple |
|---|---|---|---|
| Tareas exitosas | 30% | ✅ | Flujo completo: publicar → buscar → agendar |
| Autonomía del agente | 25% | ✅ | Guía al usuario en 7 pasos sin intervención humana |
| Uso de herramientas | 15% | ✅ | 5 herramientas con function calling real + Supabase |
| Gestión de ambigüedad | 10% | ✅ | Repregunta datos faltantes, detecta contradicciones |
| Cero alucinaciones | 10% | ✅ | Guardrail + prompt + temperature=0.3 + Supabase real |
| UX | 5% | ✅ | WebSocket streaming, mensaje de bienvenida, tono claro |
| Creatividad | 5% | ✅ | Sugerencia de ampliar radio, OpenStreetMap real |

### Dependencias bloqueantes para producción

| Dependencia | Equipo | Descripción |
|---|---|---|
| Auth (JWT) | Backend | Pasar `usuario_id` desde Supabase Auth al agente |
| UI de chat | Frontend | Conectarse a `ws://localhost:8000/ws` (WebSocket) |
| Email de confirmación | Integraciones | Enviar email cuando `agendar_retiro` devuelva éxito |
| API keys en CI | DevOps | Agregar `KOSTRA_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` a secrets |

### Credenciales

```
# LLM
KOSTRA_API_KEY = sk-1pR89DLFsv8yAAMm3PnAFw
Base URL       = https://ai.kostra.cloud/v1
Modelo         = glm-5.2

# Supabase
SUPABASE_URL   = https://tgxseiaqebedzlgnutmm.supabase.co
SUPABASE_KEY   = sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8
```

> **No commitear las API keys al repo.** Usar variables de entorno.

---

## 6. UX/UI — Wireframes del chat

El agente devuelve texto en markdown. El frontend debe renderizarlo con un parser markdown.

### Pantalla de chat — elementos necesarios

```
┌─────────────────────────────────────┐
│  ♻️ EcoMatch                        │  ← Header
├─────────────────────────────────────┤
│                                     │
│  [EcoMatch] 👋 ¡Hola! Soy EcoMatch  │  ← Mensaje de bienvenida
│  ...                                │
│                                     │
│  [Tú] Tengo 15 m3 de escombros...   │  ← Mensaje usuario (derecha)
│                                     │
│  [EcoMatch] Buscando receptores...  │  ← Status tool_start
│  [EcoMatch] ¡Tu oferta fue          │  ← Streaming token a token
│  registrada! Encontré 3 receptores: │     (efecto typing en tiempo real)
│  1. **Recicladora Norte** ...       │
│                                     │
├─────────────────────────────────────┤
│  [Input de texto............] [▶]   │  ← Input + botón enviar
└─────────────────────────────────────┘
```

### Colores sugeridos (según documento maestro)

- Fondo: `#F5F5F0` (verde claro/tierra)
- Mensajes agente: `#E8F5E9` (verde claro)
- Mensajes usuario: `#C8E6C9` (verde medio)
- Acento: `#2E7D32` (verde oscuro)
- Texto: `#1B5E20`

---

## Resumen

La capa de IA está lista y conectada a Supabase. Lo que falta para producción es:

1. **Backend** pasa el `usuario_id` desde Supabase Auth al agente
2. **Frontend** se conecta a `ws://localhost:8000/ws` (WebSocket streaming)
3. **Integraciones** configura el email de confirmación con SendGrid
4. **DevOps** pone las API keys en CI y levanta la API en el server

Cualquier duda, revisar `ia/README.md` o los logs en `ia/logs/agent.log`.
