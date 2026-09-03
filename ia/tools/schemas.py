"""
Definición de Tools (Function Calling) para el Agente EcoMatch.
Cada herramienta tiene su esquema JSON Schema para GLM 5.2 y su implementación mock.

El Backend (rol 3) reemplazará las funciones mock por llamadas reales a la API REST.
Por ahora los mocks simulan respuestas de la BD para que el agente funcione end-to-end.
"""
from .implementations import (
    buscar_receptores_impl,
    crear_oferta_residuo_impl,
    agendar_retiro_impl,
    calcular_distancia_impl,
    obtener_historial_usuario_impl,
)

# ── Esquemas de herramientas para Function Calling ──────────────────────────
# Formato compatible con GLM 5.2 (Zhipu AI) — igual al formato OpenAI tools

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "buscar_receptores",
            "description": (
                "Busca receptores de residuos en la base de datos que acepten el material "
                "indicado dentro de un radio específico desde la ubicación del generador. "
                "Devuelve solo receptores reales registrados en la plataforma."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "material": {
                        "type": "string",
                        "description": "Tipo de residuo: escombros, madera, plastico, carton, metal, vidrio, organico, electronicos, textil",
                        "enum": [
                            "escombros", "madera", "plastico", "carton",
                            "metal", "vidrio", "organico", "electronicos", "textil",
                        ],
                    },
                    "radio_km": {
                        "type": "number",
                        "description": "Radio de búsqueda en kilómetros desde la ubicación del generador",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "ubicacion": {
                        "type": "string",
                        "description": "Dirección o zona de origen del residuo",
                    },
                },
                "required": ["material", "radio_km", "ubicacion"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_oferta_residuo",
            "description": (
                "Registra una nueva oferta de residuo en la base de datos. "
                "Debe llamarse solo cuando el usuario ha proporcionado todos los datos obligatorios."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "material": {
                        "type": "string",
                        "description": "Tipo de residuo",
                        "enum": [
                            "escombros", "madera", "plastico", "carton",
                            "metal", "vidrio", "organico", "electronicos", "textil",
                        ],
                    },
                    "volumen": {
                        "type": "string",
                        "description": "Cantidad del residuo, ej: '15 m3', '500 kg', '2 toneladas'",
                    },
                    "ubicacion": {
                        "type": "string",
                        "description": "Dirección donde se encuentra el residuo para retiro",
                    },
                    "tipo_generador": {
                        "type": "string",
                        "description": "Tipo de generador del residuo",
                        "enum": ["constructora", "pyme", "persona_natural"],
                    },
                    "notas": {
                        "type": "string",
                        "description": "Notas adicionales sobre el estado del residuo, restricciones de acceso, etc.",
                    },
                },
                "required": ["material", "volumen", "ubicacion", "tipo_generador"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "agendar_retiro",
            "description": (
                "Coordina y agenda el retiro de un residuo entre un generador y un receptor. "
                "Requiere confirmación previa del usuario."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "receptor_id": {
                        "type": "integer",
                        "description": "ID del receptor devuelto por buscar_receptores",
                    },
                    "oferta_id": {
                        "type": "integer",
                        "description": "ID de la oferta creada con crear_oferta_residuo",
                    },
                    "fecha": {
                        "type": "string",
                        "description": "Fecha del retiro en formato YYYY-MM-DD",
                    },
                    "hora": {
                        "type": "string",
                        "description": "Hora del retiro en formato HH:MM (24h)",
                    },
                },
                "required": ["receptor_id", "oferta_id", "fecha", "hora"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calcular_distancia",
            "description": "Calcula la distancia en kilómetros entre dos direcciones.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origen": {
                        "type": "string",
                        "description": "Dirección de origen",
                    },
                    "destino": {
                        "type": "string",
                        "description": "Dirección de destino",
                    },
                },
                "required": ["origen", "destino"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_historial_usuario",
            "description": "Obtiene el historial de ofertas y retiros del usuario actual.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID del usuario en la base de datos",
                    },
                },
                "required": ["user_id"],
            },
        },
    },
]

# ── Dispatch table: nombre -> implementación ────────────────────────────────
TOOL_DISPATCH = {
    "buscar_receptores": buscar_receptores_impl,
    "crear_oferta_residuo": crear_oferta_residuo_impl,
    "agendar_retiro": agendar_retiro_impl,
    "calcular_distancia": calcular_distancia_impl,
    "obtener_historial_usuario": obtener_historial_usuario_impl,
}


def ejecutar_tool(name: str, arguments: dict) -> str:
    """Ejecuta una herramienta por nombre. Retorna el resultado como string JSON."""
    import json

    if name not in TOOL_DISPATCH:
        return json.dumps({"error": f"Herramienta '{name}' no existe."})
    try:
        result = TOOL_DISPATCH[name](**arguments)
        return json.dumps(result, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": f"Error ejecutando {name}: {e}"})
