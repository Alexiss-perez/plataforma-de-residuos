# Agente EcoMatch — Capa de Inteligencia Artificial (GLM 5.2)

Rol: **Ingeniero de IA** — Orquestador logístico para economía circular.

## Estructura

```
ia/
├── ecomatch_agent.py       # Script principal — loop de chat + tool calling
├── prompts/
│   └── system_prompt.md    # System Prompt (corazón del agente)
├── tools/
│   ├── schemas.py          # Esquemas JSON de Function Calling para GLM 5.2
│   ├── implementations.py  # Implementaciones MOCK (Backend las reemplaza)
│   └── __init__.py
├── tests/
│   ├── test_01_ambiguedad_volumen_faltante.json
│   ├── test_02_ambiguedad_madera_tipo.json
│   ├── test_03_flujo_completo.json
│   ├── test_04_cero_alucinaciones.json
│   ├── test_05_fuera_de_dominio.json
│   ├── test_06_prompt_confuso_lenguaje_informal.json
│   ├── test_07_info_contradictoria.json
│   ├── test_08_no_hay_receptores.json
│   ├── test_09_multi_turn_ambiguedad_resuelta.json
│   └── test_10_solicitar_ley_o_regulacion.json
├── requirements.txt
└── README.md
```

## Setup

```bash
cd ia/
pip install -r requirements.txt
export KOSTRA_API_KEY="tu-api-key-aqui"
```

El agente usa el SDK `openai` apuntando a `https://ai.kostra.cloud/v1` (OpenAI-compatible).
El modelo es `glm-5.2`.

## Uso

**Chat interactivo:**
```bash
python ecomatch_agent.py
```

**Ejecutar tests automáticos (10 casos):**
```bash
python ecomatch_agent.py --test
```

## Casos de Prueba

| # | Test | Rúbrica que valida |
|---|------|-------------------|
| 01 | Ambigüedad — volumen faltante | Gestión de ambigüedad (10%) |
| 02 | Ambigüedad — tipo de madera | Gestión de ambigüedad (10%) |
| 03 | Flujo completo feliz | Tareas exitosas (30%) |
| 04 | Cero alucinaciones | Fiabilidad (10%) |
| 05 | Fuera de dominio | Comportamiento del agente (25%) |
| 06 | Lenguaje informal/confuso | Gestión de ambigüedad (10%) |
| 07 | Info contradictoria | Gestión de ambigüedad (10%) |
| 08 | No hay receptores | Fiabilidad (10%) |
| 09 | Multi-turn ambigüedad resuelta | Autonomía (25%) |
| 10 | Solicitar ley/regulación | Fiabilidad (10%) |

## Integración con Backend

Las funciones en `tools/implementations.py` son MOCKS. El equipo de Backend
debe reemplazarlas con llamadas reales a la API REST:

```python
# Antes (mock)
def buscar_receptores_impl(material, radio_km, ubicacion):
    ...

# Después (real)
def buscar_receptores_impl(material, radio_km, ubicacion):
    response = requests.get(f"{API_URL}/receptores", params={...})
    return response.json()
```

## Política de Cero Alucinaciones

El agente está configurado con `temperature=0.3` para minimizar alucinaciones.
El System Prompt prohíbe explícitamente inventar empresas, direcciones, o leyes.
Las tools solo devuelven datos de la BD real.
