"""Formularios estructurados por tipo de material para EcoMatch.

Evita errores de tipeo, reduce carga conversacional y mejora UX.
El frontend renderiza los campos según el tipo de material.
"""
from __future__ import annotations

# ── Campos comunes a todos los formularios ─────────────────────────────────
def _campos_comunes() -> list:
    return [
        {
            "name": "ubicacion",
            "label": "📍 Ubicación para retiro",
            "type": "text",
            "placeholder": "Ej: Av. Principal 123, Santiago",
            "required": True,
        },
        {
            "name": "tipo_generador",
            "label": "Tipo de generador",
            "type": "select",
            "options": [
                {"value": "constructora", "label": "🏗️ Constructora"},
                {"value": "pyme", "label": "🏢 Pyme"},
                {"value": "persona_natural", "label": "👤 Persona natural"},
            ],
            "required": True,
        },
    ]


# ── Formularios por tipo de material ───────────────────────────────────────
FORMULARIOS: dict[str, dict] = {
    "textil": {
        "material": "textil",
        "titulo": "👕 Formulario de desecho textil",
        "descripcion": "Completa los datos para publicar tu desecho textil.",
        "campos": [
            {"name": "volumen", "label": "¿Cuántos kilos tienes?", "type": "number", "unit": "kg", "placeholder": "Ej: 50", "required": True},
            {"name": "subtipo", "label": "Tipo de desecho textil", "type": "select", "options": [
                {"value": "ropa", "label": "Ropa"},
                {"value": "retales", "label": "Retales de confección"},
                {"value": "telas_industriales", "label": "Telas industriales"},
                {"value": "calzado", "label": "Calzado"},
            ], "required": True},
            {"name": "condicion", "label": "¿En qué condición está?", "type": "select", "options": [
                {"value": "donable", "label": "✅ Apto para donación"},
                {"value": "reutilizable", "label": "♻️ Reutilizable (destruir y dar uso distinto)"},
                {"value": "inservible", "label": "❌ Inservible (solo reciclaje industrial)"},
            ], "required": True},
            *_campos_comunes(),
            {"name": "notas", "label": "Notas adicionales (opcional)", "type": "textarea", "placeholder": "Ej: Ropa de invierno, ropa infantil, etc.", "required": False},
        ],
    },
    "vidrio": {
        "material": "vidrio",
        "titulo": "🍾 Formulario de vidrio",
        "descripcion": "Completa los datos para publicar tu residuo de vidrio.",
        "campos": [
            {"name": "volumen", "label": "¿Cuántos kilos tienes?", "type": "number", "unit": "kg", "placeholder": "Ej: 30", "required": True},
            {"name": "estado", "label": "Estado del vidrio", "type": "select", "options": [
                {"value": "entero", "label": "Entero (botellas, frascos)"},
                {"value": "roto", "label": "Roto"},
            ], "required": True},
            {"name": "separacion_color", "label": "Separación por color", "type": "select", "options": [
                {"value": "separado", "label": "Separado por color (verde, ámbar, transparente)"},
                {"value": "mezclado", "label": "Mezclado"},
            ], "required": True},
            *_campos_comunes(),
        ],
    },
    "carton": {
        "material": "carton",
        "titulo": "📦 Formulario de cartón",
        "descripcion": "Completa los datos para publicar tu residuo de cartón.",
        "campos": [
            {"name": "volumen", "label": "¿Cuánto tienes?", "type": "number", "unit": "kg", "placeholder": "Ej: 100", "required": True},
            {"name": "tipo_carton", "label": "Tipo de cartón", "type": "select", "options": [
                {"value": "corrugado", "label": "Cartón corrugado (cajas)"},
                {"value": "plano", "label": "Cartón plano"},
                {"value": "mezclado", "label": "Mezclado"},
            ], "required": True},
            {"name": "condicion", "label": "Estado del cartón", "type": "select", "options": [
                {"value": "limpio", "label": "✅ Limpio (sin grasa, cintas o staples)"},
                {"value": "contaminado", "label": "⚠️ Contaminado"},
            ], "required": True},
            *_campos_comunes(),
        ],
    },
    "plastico": {
        "material": "plastico",
        "titulo": "♻️ Formulario de plástico",
        "descripcion": "Completa los datos para publicar tu residuo plástico.",
        "campos": [
            {"name": "volumen", "label": "¿Cuántos kilos tienes?", "type": "number", "unit": "kg", "placeholder": "Ej: 80", "required": True},
            {"name": "tipo_plastico", "label": "Tipo de plástico", "type": "select", "options": [
                {"value": "pet", "label": "PET (botellas de bebida)"},
                {"value": "hdpe", "label": "HDPE (envases de detergentes)"},
                {"value": "bolsas", "label": "Bolsas plásticas"},
                {"value": "film", "label": "Film / stretch"},
                {"value": "mezclado", "label": "Mezclado"},
            ], "required": True},
            {"name": "condicion", "label": "Estado del plástico", "type": "select", "options": [
                {"value": "limpio_separado", "label": "✅ Limpio y separado"},
                {"value": "mezclado", "label": "⚠️ Mezclado con otros materiales"},
            ], "required": True},
            *_campos_comunes(),
        ],
    },
    "metal": {
        "material": "metal",
        "titulo": "🔩 Formulario de metal",
        "descripcion": "Completa los datos para publicar tu residuo metálico.",
        "campos": [
            {"name": "volumen", "label": "¿Cuánto tienes?", "type": "number", "unit": "kg", "placeholder": "Ej: 500", "required": True},
            {"name": "tipo_metal", "label": "Tipo de metal", "type": "select", "options": [
                {"value": "hierro", "label": "Hierro / acero"},
                {"value": "aluminio", "label": "Aluminio"},
                {"value": "cobre", "label": "Cobre"},
                {"value": "lata", "label": "Lata"},
                {"value": "mezclado", "label": "Mezclado"},
            ], "required": True},
            {"name": "condicion", "label": "Estado del metal", "type": "select", "options": [
                {"value": "limpio", "label": "✅ Limpio (sin pintura ni recubrimientos)"},
                {"value": "contaminado", "label": "⚠️ Contaminado"},
            ], "required": True},
            *_campos_comunes(),
        ],
    },
    "escombros": {
        "material": "escombros",
        "titulo": "🧱 Formulario de escombros",
        "descripcion": "Completa los datos para publicar tu residuo de escombros.",
        "campos": [
            {"name": "volumen", "label": "¿Cuál es el volumen aproximado?", "type": "number", "unit": "m³", "placeholder": "Ej: 15", "required": True},
            {"name": "tipo_escombro", "label": "Tipo de escombro", "type": "select", "options": [
                {"value": "limpio", "label": "Limpio (solo concreto/ladrillo)"},
                {"value": "mezclado", "label": "Mezclado con otros materiales"},
            ], "required": True},
            {"name": "carga", "label": "Método de carga", "type": "select", "options": [
                {"value": "camioneta", "label": "🚛 Camioneta"},
                {"value": "camion_grua", "label": "🚚 Camión grúa"},
                {"value": "manual", "label": "💪 Carga manual"},
            ], "required": True},
            *_campos_comunes(),
        ],
    },
    "madera": {
        "material": "madera",
        "titulo": "🪵 Formulario de madera",
        "descripcion": "Completa los datos para publicar tu residuo de madera.",
        "campos": [
            {"name": "volumen", "label": "¿Cuánto tienes?", "type": "number", "unit": "kg", "placeholder": "Ej: 200", "required": True},
            {"name": "tipo_madera", "label": "Tipo de madera", "type": "select", "options": [
                {"value": "virgen", "label": "🌳 Virgen (sin tratar)"},
                {"value": "tratada", "label": "⚠️ Tratada (con pintura, barniz o químicos)"},
            ], "required": True},
            {"name": "formato", "label": "Formato de la madera", "type": "select", "options": [
                {"value": "piezas_grandes", "label": "Piezas grandes (vigas, tablas)"},
                {"value": "piezas_pequenas", "label": "Piezas pequeñas (astillas, recortes)"},
            ], "required": True},
            *_campos_comunes(),
        ],
    },
    "electronicos": {
        "material": "electronicos",
        "titulo": "💻 Formulario de residuos electrónicos",
        "descripcion": "Completa los datos para publicar tu residuo electrónico.",
        "campos": [
            {"name": "volumen", "label": "¿Cuántas unidades tienes?", "type": "number", "unit": "unidades", "placeholder": "Ej: 10", "required": True},
            {"name": "tipo_electronico", "label": "Tipo de equipo", "type": "select", "options": [
                {"value": "computadores", "label": "Computadores / laptops"},
                {"value": "monitores", "label": "Monitores / pantallas"},
                {"value": "cables", "label": "Cables"},
                {"value": "baterias", "label": "Baterías"},
                {"value": "celulares", "label": "Celulares"},
                {"value": "mezclado", "label": "Mezclado"},
            ], "required": True},
            {"name": "estado", "label": "Estado de los equipos", "type": "select", "options": [
                {"value": "funcionando", "label": "✅ Funcionando"},
                {"value": "fuera_uso", "label": "❌ Fuera de uso"},
            ], "required": True},
            *_campos_comunes(),
        ],
    },
    "organico": {
        "material": "organico",
        "titulo": "🍂 Formulario de residuos orgánicos",
        "descripcion": "Completa los datos para publicar tu residuo orgánico.",
        "campos": [
            {"name": "volumen", "label": "¿Cuántos kilos tienes?", "type": "number", "unit": "kg", "placeholder": "Ej: 20", "required": True},
            {"name": "subtipo_organico", "label": "Tipo de residuo orgánico", "type": "select", "options": [
                {"value": "restos_comida", "label": "Restos de comida"},
                {"value": "jardin", "label": "Residuos de jardín (hojas, ramas)"},
                {"value": "aceite_vegetal", "label": "Aceite vegetal"},
                {"value": "otros", "label": "Otros"},
            ], "required": True},
            *_campos_comunes(),
        ],
    },
}

FORMULARIO_INICIAL = {
    "form_id": "seleccion_material",
    "titulo": "♻️ ¿Qué tipo de residuo quieres publicar?",
    "descripcion": "Selecciona el tipo de residuo para completar el formulario.",
    "campos": [
        {"name": "material", "label": "Tipo de residuo", "type": "select", "options": [
            {"value": "textil", "label": "👕 Textil"},
            {"value": "vidrio", "label": "🍾 Vidrio"},
            {"value": "carton", "label": "📦 Cartón"},
            {"value": "plastico", "label": "♻️ Plástico"},
            {"value": "metal", "label": "🔩 Metal"},
            {"value": "escombros", "label": "🧱 Escombros"},
            {"value": "madera", "label": "🪵 Madera"},
            {"value": "electronicos", "label": "💻 Electrónicos"},
            {"value": "organico", "label": "🍂 Orgánico"},
        ], "required": True},
    ],
}


def obtener_formulario(material: str) -> dict | None:
    form = FORMULARIOS.get(material)
    if not form:
        return None
    return {"form_id": f"publicar_{material}", "titulo": form["titulo"], "descripcion": form["descripcion"], "material": material, "campos": form["campos"]}


def obtener_formulario_inicial() -> dict:
    return FORMULARIO_INICIAL


def validar_formulario(material: str, datos: dict) -> dict:
    form = obtener_formulario(material)
    if not form:
        return {"ok": False, "errors": [f"No existe formulario para material '{material}'"]}

    errors = []
    data_clean = {}

    for campo in form["campos"]:
        name = campo["name"]
        required = campo.get("required", False)
        value = datos.get(name)

        if required and (value is None or value == ""):
            errors.append(f"El campo '{campo['label']}' es obligatorio")
            continue

        if value is not None:
            if campo["type"] == "number":
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    errors.append(f"El campo '{campo['label']}' debe ser un número")
                    continue
            if campo["type"] == "select":
                valid_values = [opt["value"] for opt in campo["options"]]
                if value not in valid_values:
                    errors.append(f"Valor inválido para '{campo['label']}'")
                    continue
            data_clean[name] = value

    if errors:
        return {"ok": False, "errors": errors}
    return {"ok": True, "data": data_clean}
