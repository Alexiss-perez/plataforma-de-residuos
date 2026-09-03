# Guía de Integración — Capa de IA (EcoMatch)

> **Para:** Backend, Frontend, Integraciones, QA/DevOps, PM
> **De:** Ingeniero de IA
> **Estado:** Listo para integrar

---

## ¿Qué está hecho?

La capa de IA está **100% funcional** y lista para que el resto del equipo se conecte.
El agente funciona con GLM 5.2 vía la API de Kostra, tiene 5 herramientas (function calling),
guardrail anti-alucinaciones, API REST y 11 tests que pasan.

```
ia/
├── ecomatch_agent.py       # Agente principal (chat + tool calling + guardrail)
├── api.py                  # API REST FastAPI (endpoint /chat para el frontend)
├── guardrail.py            # Capa anti-alucinaciones (valida respuestas antes de enviarlas)
├── prompts/
│   └── system_prompt.md    # System Prompt (identidad, reglas, flujo)
├── tools/
│   ├── schemas.py          # Esquemas JSON de las 5 herramientas
│   ├── implementations.py  # Implementaciones (mocks + OpenStreetMap real)
│   └── __init__.py
├── tests/                  # 11 casos de prueba
├── logs/                   # Logs de conversaciones (se generan automáticamente)
├── requirements.txt
└── README.md
```

---

## 1. Backend — Cómo reemplazar los mocks por la BD real

Las herramientas en `ia/tools/implementations.py` son **mocks** que simulan la base de datos.
Debes reemplazarlas con llamadas reales a tu API REST.

### Esquema de BD esperado

```sql
-- Tabla: usuarios
CREATE TABLE usuarios (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(255) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    tipo        VARCHAR(50) CHECK (tipo IN ('constructora', 'pyme', 'persona_natural')),
    direccion   TEXT,
    telefono    VARCHAR(50),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Tabla: receptores
CREATE TABLE receptores (
    id                    SERIAL PRIMARY KEY,
    nombre                VARCHAR(255) NOT NULL,
    tipo                  VARCHAR(50) CHECK (tipo IN ('planta_reciclaje', 'ong', 'pyme')),
    materiales_aceptados  TEXT[],  -- ej: ['escombros', 'metal', 'plastico']
    direccion             TEXT NOT NULL,
    telefono              VARCHAR(50),
    capacidad_disponible  VARCHAR(100),
    lat                   FLOAT,
    lon                   FLOAT
);

-- Tabla: ofertas_residuo
CREATE TABLE ofertas_residuo (
    id              SERIAL PRIMARY KEY,
    usuario_id      INT REFERENCES usuarios(id),
    material        VARCHAR(50) NOT NULL,
    volumen         VARCHAR(100) NOT NULL,
    ubicacion       TEXT NOT NULL,
    tipo_generador  VARCHAR(50) NOT NULL,
    notas           TEXT,
    estado          VARCHAR(20) DEFAULT 'publicada',
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Tabla: retiros
CREATE TABLE retiros (
    id          SERIAL PRIMARY KEY,
    oferta_id   INT REFERENCES ofertas_residuo(id),
    receptor_id INT REFERENCES receptores(id),
    fecha       DATE NOT NULL,
    hora        TIME NOT NULL,
    estado      VARCHAR(20) DEFAULT 'agendado',
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### Reemplazar los mocks

Cada función mock en `implementations.py` tiene un comentario indicando cómo reemplazarla.
Ejemplo para `buscar_receptores`:

```python
# ANTES (mock) — en ia/tools/implementations.py
def buscar_receptores_impl(material: str, radio_km: float, ubicacion: str) -> dict:
    receptores_encontrados = [...]  # lista hardcodeada
    return {"total": len(...), "receptores": receptores_encontrados}

# DESPUÉS (real) — el Backend reemplaza con llamada a la BD
import requests

API_URL = "http://localhost:3000/api"  # URL del backend

def buscar_receptores_impl(material: str, radio_km: float, ubicacion: str) -> dict:
    response = requests.get(f"{API_URL}/receptores", params={
        "material": material,
        "radio_km": radio_km,
        "ubicacion": ubicacion,
    })
    return response.json()
```

**Las 5 funciones que debes conectar:**

| Función mock | Endpoint sugerido | Tabla BD |
|---|---|---|
| `buscar_receptores_impl` | `GET /api/receptores?material=&radio_km=&ubicacion=` | `receptores` |
| `crear_oferta_residuo_impl` | `POST /api/ofertas` | `ofertas_residuo` |
| `agendar_retiro_impl` | `POST /api/retiros` | `retiros` |
| `obtener_historial_usuario_impl` | `GET /api/usuarios/{id}/historial` | `ofertas_residuo` + `retiros` |
| `calcular_distancia_impl` | Ya está conectada (OpenStreetMap real) | — |

### Datos mock actuales (para que sepas qué esperar)

Los 5 receptores en la BD mock:

| ID | Nombre | Materiales | Dirección |
|---|---|---|---|
| 1 | Recicladora Norte | escombros, metal, plastico | Av. Norte 450 |
| 2 | ONG Construye Verde | madera, escombros, metal | Calle Verde 12 |
| 3 | Planta Procesadora Sur | escombros, vidrio, plastico | Av. Sur 890 |
| 4 | Cartoneros Unidos | carton, plastico | Pasaje Reciclaje 7 |
| 5 | Reutiliza Textil | textil, madera | Calle Tela 99 |

Materiales válidos (enum): `escombros, madera, plastico, carton, metal, vidrio, organico, electronicos, textil`

---

## 2. Frontend — Cómo conectarse al agente

### Opción A: Via API REST (recomendado)

Levanta la API del agente:

```bash
cd ia/
uvicorn api:app --port 8000
```

Endpoints disponibles:

```javascript
// Iniciar conversación o enviar mensaje
POST http://localhost:8000/chat
Content-Type: application/json

// Request
{
  "session_id": "abc123",   // opcional, si no se envía se crea una nueva
  "message": "Tengo 15 m3 de escombros en Av. Principal 123, soy constructora"
}

// Response
{
  "session_id": "abc123",
  "response": "¡Tu oferta fue registrada! Encontré 3 receptores...",
  "tool_calls": [],
  "timestamp": "2025-09-03T13:10:00"
}
```

```javascript
// Reiniciar conversación
POST http://localhost:8000/chat/reset
{
  "session_id": "abc123"
}

// Obtener historial de la sesión
GET http://localhost:8000/chat/abc123/history

// Health check
GET http://localhost:8000/health
```

### Ejemplo de integración en React

```javascript
async function sendMessage(message, sessionId) {
  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  const data = await res.json();
  return data;  // { session_id, response, timestamp }
}

// Uso:
// 1. Primer mensaje (sin session_id) → crea sesión
// 2. Guardar session_id en estado del componente
// 3. Mensajes siguientes → enviar mismo session_id
```

### Opción B: Chat embebido (sin API REST)

Si prefieren no usar la API REST, pueden importar el agente directamente:

```python
from ecomatch_agent import enviar_mensaje, SYSTEM_PROMPT

messages = [{"role": "system", "content": SYSTEM_PROMPT}]
messages.append({"role": "user", "content": "Tengo escombros..."})
result = enviar_mensaje(messages)
print(result["content"])  # respuesta del agente
```

### Mensaje de bienvenida

El agente tiene un mensaje de bienvenida. Muéstralo al cargar la interfaz de chat:

```
👋 ¡Hola! Soy EcoMatch, tu agente de economía circular. ♻️

Puedo ayudarte a:
1. Publicar residuos que quieres que retiren de tu ubicación
2. Buscar receptores cerca de ti (ONGs, plantas de reciclaje, pymes)
3. Coordinar el retiro entre tú y el receptor

Cuéntame: ¿qué residuo tienes y dónde estás ubicado?
```

Si el usuario envía "hola", "hi" o "inicio", la API devuelve este mensaje automáticamente.

### Manejo de estados en el frontend

| Estado | Cuándo | UX sugerida |
|---|---|---|
| `loading` | Esperando respuesta del agente | Spinner o "EcoMatch está escribiendo..." |
| `success` | Respuesta recibida | Mostrar `response` en el chat |
| `error` | API caída | "El agente no está disponible. Intenta más tarde." |
| `tool_calling` | El agente está usando herramientas | "Buscando receptores..." (opcional) |

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
  "retiro_id": 1,
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
python ecomatch_agent.py --test
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

Formato:
```
2025-09-03 13:10:00 [INFO] [TOOL] buscar_receptores({'material': 'escombros', ...})
2025-09-03 13:10:00 [INFO] [TOOL RESULT] {"total": 3, ...}
2025-09-03 13:10:01 [WARNING] GUARDRAIL bloqueó: Receptor no reconocido
```

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
```

---

## 5. PM / Product Owner — Estado del apartado de IA

### Cobertura de la rúbrica

| Criterio | Peso | Estado | Cómo se cumple |
|---|---|---|---|
| Tareas exitosas | 30% | ✅ | Flujo completo: publicar → buscar → agendar |
| Autonomía del agente | 25% | ✅ | Guía al usuario en 7 pasos sin intervención humana |
| Uso de herramientas | 15% | ✅ | 5 herramientas con function calling real |
| Gestión de ambigüedad | 10% | ✅ | Repregunta datos faltantes, detecta contradicciones |
| Cero alucinaciones | 10% | ✅ | Guardrail + prompt + temperature=0.3 + tools reales |
| UX | 5% | ✅ | Mensaje de bienvenida, tono claro, formato lista |
| Creatividad | 5% | ✅ | Sugerencia de ampliar radio, OpenStreetMap real |

### Dependencias bloqueantes para producción

| Dependencia | Equipo | Descripción |
|---|---|---|
| BD real | Backend | Reemplazar mocks en `implementations.py` por endpoints reales |
| UI de chat | Frontend | Conectarse a `POST /chat` y manejar `session_id` |
| Email de confirmación | Integraciones | Enviar email cuando `agendar_retiro` devuelva éxito |
| API key en CI | DevOps | Agregar `KOSTRA_API_KEY` a secrets de GitHub |

### API Key

```
KOSTRA_API_KEY = sk-1pR89DLFsv8yAAMm3PnAFw
Base URL       = https://ai.kostra.cloud/v1
Modelo         = glm-5.2
```

> **No commitear la API key al repo.** Usar variable de entorno.

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
│  [EcoMatch] ¡Tu oferta fue          │  ← Respuesta agente (izquierda)
│  registrada! Encontré 3 receptores: │     (renderizar markdown)
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

La capa de IA está lista. Lo que falta para producción es:

1. **Backend** conecta los mocks a la BD real
2. **Frontend** se conecta a `POST /chat`
3. **Integraciones** configura el email de confirmación
4. **DevOps** pone la API key en CI y levanta la API en el server

Cualquier duda, revisar `ia/README.md` o los logs en `ia/logs/agent.log`.
