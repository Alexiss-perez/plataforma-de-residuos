# Resumen de Trabajo — Capa de IA (EcoMatch)

> **Rol:** Ingeniero de IA
> **Proyecto:** Plataforma EcoMatch — Economía circular
> **Modelo:** GLM 5.2 vía Kostra (OpenAI-compatible)
> **Fecha:** Septiembre 2026

---

## 1. System Prompt

**Archivo:** `prompts/system_prompt.md`

Define la identidad, reglas y comportamiento del agente:

- **Identidad:** EcoMatch, agente de orquestación logística para economía circular
- **Cero alucinaciones (10% rúbrica):** prohibición explícita de inventar empresas, direcciones, teléfonos o leyes. Solo datos reales de la BD
- **Clasificación de residuos:** orgánico / inorgánico con 9 subtipos (textil, vidrio, cartón, plástico, metal, escombros, madera, electrónicos, orgánico)
- **Gestión de ambigüedad (10% rúbrica):** preguntas específicas por tipo de material. Nunca asume valores por defecto
- **Formularios estructurados:** la inserción de datos se hace via formularios, no por chat libre, para evitar errores de tipeo y reducir carga conversacional
- **Flujo obligatorio de 8 pasos:** detectar intención → clasificar → enviar formulario → recibir datos → invocar tools → presentar opciones → coordinar retiro → confirmar
- **Restricciones de dominio:** declina preguntas fuera de gestión de residuos
- **Tono y estilo:** profesional pero cercano, emojis moderados, formato lista

---

## 2. Function Calling — 5 Herramientas

**Archivos:** `tools/schemas.py`, `tools/implementations.py`

| Herramienta | Descripción | Conexión |
|---|---|---|
| `buscar_receptores` | Busca receptores que acepten el material en un radio | ✅ Supabase real |
| `crear_oferta_residuo` | Registra una oferta de residuo | ✅ Supabase real |
| `agendar_retiro` | Coordinar retiro entre generador y receptor | ✅ Supabase real |
| `calcular_distancia` | Distancia entre dos direcciones | ✅ OpenStreetMap Nominatim (gratis, sin API key) |
| `obtener_historial_usuario` | Historial de ofertas y retiros | ✅ Supabase real (RPC function) |

Cada herramienta tiene esquema JSON Schema compatible con GLM 5.2.

---

## 3. Base de Datos — Supabase

**Proyecto:** `tgxseiaqebedzlgnutmm`
**URL:** `https://tgxseiaqebedzlgnutmm.supabase.co`

### Tablas creadas

| Tabla | PK | RLS | Registros | Descripción |
|---|---|---|---|---|
| `usuarios` | UUID | ✅ | 0 | nombre, email, tipo (constructora/pyme/persona_natural), direccion, telefono |
| `receptores` | SERIAL | ✅ | 5 | nombre, tipo (planta_reciclaje/ong/pyme), materiales_aceptados[], direccion, telefono, capacidad, lat, lon |
| `ofertas_residuo` | UUID | ✅ | 0 | FK usuarios, material, volumen, ubicacion, tipo_generador, notas, estado |
| `retiros` | UUID | ✅ | 0 | FK ofertas + receptores, fecha, hora, estado |

### RLS Policies (13 total)

- **usuarios:** cada usuario ve/edita solo su perfil
- **receptores:** lectura pública, escritura solo constructoras
- **ofertas_residuo:** cada usuario ve/edita sus propias ofertas
- **retiros:** cada usuario ve/edita retiros de sus propias ofertas

### RPC Function

```sql
get_user_retiros(p_user_id UUID) — join retiros + ofertas + receptores
```
Configurada con `SECURITY INVOKER` y `search_path = public` (0 warnings de seguridad).

### Receptores seed insertados

| ID | Nombre | Materiales |
|---|---|---|
| 1 | Recicladora Norte | escombros, metal, plastico |
| 2 | ONG Construye Verde | madera, escombros, metal |
| 3 | Planta Procesadora Sur | escombros, vidrio, plastico |
| 4 | Cartoneros Unidos | carton, plastico |
| 5 | Reutiliza Textil | textil, madera |

---

## 4. Guardrail Anti-Alucinaciones

**Archivo:** `guardrail.py`

Capa de validación que intercepta la respuesta del LLM **antes** de enviarla al usuario:

1. **Leyes/decretos:** bloquea menciones a números de ley específicos
2. **Receptores inválidos:** valida que los receptores mencionados existan en Supabase (carga dinámica)
3. **Longitud excesiva:** bloquea respuestas >3000 chars (posible alucinación en cascada)
4. **Teléfonos sospechosos:** bloquea teléfonos asociados a receptores no válidos

Si bloquea, devuelve un mensaje seguro alternativo.

---

## 5. Formularios Estructurados

**Archivo:** `tools/formularios.py`

9 formularios (uno por material) + formulario inicial de selección:

| Material | Campos específicos |
|---|---|
| textil | volumen, subtipo (ropa/retales/telas/calzado), condición (donable/reutilizable/inservible) |
| vidrio | volumen, estado (entero/roto), separación por color (separado/mezclado) |
| carton | volumen, tipo (corrugado/plano/mezclado), condición (limpio/contaminado) |
| plastico | volumen, tipo (PET/HDPE/bolsas/film/mezclado), condición (limpio/mezclado) |
| metal | volumen, tipo (hierro/aluminio/cobre/lata/mezclado), condición (limpio/contaminado) |
| escombros | volumen, tipo (limpio/mezclado), método de carga (camioneta/grúa/manual) |
| madera | volumen, tipo (virgen/tratada), formato (piezas grandes/pequeñas) |
| electronicos | volumen, tipo (computadores/monitores/cables/baterías/celulares), estado (funcionando/fuera de uso) |
| organico | volumen, subtipo (restos comida/jardín/aceite vegetal/otros) |

Todos incluyen: ubicación (text) + tipo de generador (select).

**Ventajas:**
- Cero errores de tipeo (selects y number inputs)
- Menos tokens (1 mensaje vs 4-5 turnos de chat)
- Mejor UX (campos predefinidos, placeholders, validación)
- Menos carga en BD (datos validados antes de insertar)

---

## 6. API — WebSocket + REST

**Archivo:** `api.py` (FastAPI)

### WebSocket `/ws` (streaming token a token)

**Acciones del cliente:**

| Acción | Descripción |
|---|---|
| `connect` | Iniciar conexión, recibe session_id + welcome |
| `message` | Enviar mensaje de chat libre |
| `get_form_inicial` | Pedir formulario de selección de material |
| `get_form` | Pedir formulario específico de un material |
| `submit_form` | Enviar formulario completado |
| `reset` | Reiniciar conversación |

**Eventos del servidor:**

| Tipo | Descripción |
|---|---|
| `connected` | Sesión creada |
| `welcome` | Mensaje de bienvenida |
| `token` | Cada token en tiempo real (efecto typing) |
| `tool_start` | El agente está invocando una herramienta |
| `tool_end` | La herramienta terminó |
| `done` | Respuesta completa |
| `form` | Formulario estructurado para renderizar |
| `form_validation_error` | Error de validación del formulario |
| `guardrail_blocked` | El guardrail bloqueó una alucinación |
| `error` | Error |

### REST (compatibilidad)

| Endpoint | Método | Descripción |
|---|---|---|
| `/chat` | POST | Chat sin streaming |
| `/chat/reset` | POST | Reiniciar sesión |
| `/chat/{id}/history` | GET | Historial de sesión |
| `/forms` | GET | Formulario inicial |
| `/forms/{material}` | GET | Formulario por material |
| `/forms/submit` | POST | Enviar formulario |
| `/health` | GET | Health check |
| `/docs` | GET | Documentación Swagger |

---

## 7. Logging

**Archivo:** `logs/agent.log` (auto-generado)

Cada interacción registra:
- Nueva sesión creada
- Mensaje del usuario
- Tools invocadas (nombre + argumentos + resultado)
- Respuesta del agente
- Bloqueos del guardrail
- Errores

---

## 8. Tipos TypeScript

**Archivo:** `types/supabase.ts`

Tipos generados desde Supabase para el frontend:
- `Database` con todas las tablas (Row, Insert, Update)
- `Tables`, `TablesInsert`, `TablesUpdate` helpers
- Function `get_user_retiros` tipada

---

## 9. Tests — 22 casos

**Directorio:** `tests/`

### Tests originales (1-11)

| # | Test | Rúbrica |
|---|---|---|
| 01 | Ambigüedad — volumen faltante | 10% ambigüedad |
| 02 | Ambigüedad — tipo de madera | 10% ambigüedad |
| 03 | Flujo completo feliz | 30% tareas |
| 04 | Cero alucinaciones | 10% fiabilidad |
| 05 | Fuera de dominio | 25% autonomía |
| 06 | Lenguaje informal/confuso | 10% ambigüedad |
| 07 | Info contradictoria | 10% ambigüedad |
| 08 | No hay receptores | 10% fiabilidad |
| 09 | Multi-turn ambigüedad resuelta | 25% autonomía |
| 10 | Solicitar ley/regulación | 10% fiabilidad |
| 11 | E2E agendar retiro | 30% tareas |

### Tests de clasificación (12-20)

| # | Test | Qué valida |
|---|---|---|
| 12 | Textil — condición | Pregunta donable vs destruir |
| 13 | Orgánico vs inorgánico | Clasifica cuando es ambiguo |
| 14 | Vidrio — separación color | Pregunta entero/roto, color |
| 15 | Plástico — tipo PET vs mezclado | Pregunta tipo específico |
| 16 | Madera — tratada vs virgen | Clasifica según tratamiento |
| 17 | Cartón — corrugado vs plano | Pregunta tipo y condición |
| 18 | Electrónicos — tipo | Pregunta tipo específico |
| 19 | Aceite — vegetal vs mineral | Clasifica orgánico |
| 20 | Metal — tipo específico | Pregunta hierro/aluminio/cobre |

### Tests de formularios (21-22)

| # | Test | Qué valida |
|---|---|---|
| 21 | Formulario textil completado | Datos estructurados → busca receptores |
| 22 | Formulario escombros completado | Datos estructurados → busca + presenta |

---

## 10. Cobertura de la Rúbrica

| Criterio | Peso | Estado | Cómo se cumple |
|---|---|---|---|
| Tareas exitosas/correctas | 30% | ✅ | Flujo completo: publicar → buscar → agendar (tests 03, 11, 22) |
| Comportamiento del agente y autonomía | 25% | ✅ | 8 pasos sin intervención humana, guía al usuario (tests 05, 09) |
| Uso de herramientas y orquestación | 15% | ✅ | 5 tools con function calling + Supabase + OpenStreetMap real |
| Gestión de ambigüedad y fallos | 10% | ✅ | Repreguntas específicas, detecta contradicciones, formularios (tests 01, 02, 06, 07, 12-20) |
| Fiabilidad y prevención de alucinaciones | 10% | ✅ | Guardrail + prompt + temperature=0.3 + Supabase real (tests 04, 08, 10) |
| Experiencia de usuario (UX) | 5% | ✅ | WebSocket streaming, formularios, mensaje de bienvenida, tono claro |
| Creatividad | 5% | ✅ | Sugerencia de ampliar radio, OpenStreetMap real, clasificación orgánico/inorgánico |

**Total: 100% de la rúbrica cubierta**

---

## 11. Configuración

### Variables de entorno

```bash
# LLM (GLM 5.2 via Kostra)
KOSTRA_API_KEY="sk-1pR89DLFsv8yAAMm3PnAFw"

# Supabase (BD real)
SUPABASE_URL="https://tgxseiaqebedzlgnutmm.supabase.co"
SUPABASE_KEY="sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8"
```

### Dependencias

```
openai>=1.0.0
fastapi>=0.100.0
uvicorn>=0.20.0
pydantic>=2.0.0
supabase>=2.0.0
```

### Comandos

```bash
# Instalar
pip install -r requirements.txt

# Chat interactivo
python ecomatch_agent.py

# Ejecutar 22 tests
python ecomatch_agent.py --test

# Levantar API (WebSocket + REST)
uvicorn api:app --port 8000
```

---

## 12. Estructura final de archivos

```
ia/
├── ecomatch_agent.py           # Agente principal (chat + streaming + tools + guardrail)
├── api.py                      # API FastAPI — WebSocket + REST + formularios
├── guardrail.py                # Anti-alucinaciones (carga receptores desde Supabase)
├── prompts/
│   └── system_prompt.md        # System Prompt (identidad, reglas, clasificación, formularios)
├── tools/
│   ├── schemas.py              # Esquemas JSON de 5 herramientas (function calling)
│   ├── implementations.py      # Implementaciones conectadas a Supabase + OpenStreetMap
│   ├── formularios.py          # 9 formularios estructurados + validación
│   └── __init__.py
├── tests/                      # 22 casos de prueba
│   ├── test_01_ambiguedad_volumen_faltante.json
│   ├── ...
│   └── test_22_formulario_escombros_completado.json
├── types/
│   └── supabase.ts             # Tipos TypeScript para el frontend
├── logs/                       # Logs de conversaciones (auto-generado)
├── requirements.txt
├── README.md
├── GUIA_INTEGRACION_EQUIPO.md  # Guía para backend, frontend, QA, PM
└── RESUMEN_TRABAJO.md          # Este documento
```

---

## 13. Pendientes para producción

| Pendiente | Equipo responsable | Descripción |
|---|---|---|
| Auth JWT | Backend | Pasar `usuario_id` desde Supabase Auth al agente |
| UI de chat | Frontend | Conectarse a `ws://localhost:8000/ws` y renderizar formularios |
| Email confirmación | Integraciones | Enviar email cuando `agendar_retiro` devuelva éxito |
| API keys en CI | DevOps | Agregar `KOSTRA_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` a secrets |
| Renderizar markdown | Frontend | El agente devuelve markdown, usar un parser |
| Renderizar formularios | Frontend | Usar los esquemas de `tools/formularios.py` para generar UI dinámica |
