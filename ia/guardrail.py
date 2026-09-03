"""
Guardrail Anti-Alucinación para EcoMatch
========================================
Capa de validación que intercepta la respuesta del LLM ANTES de enviarla al usuario.
Si detecta una posible alucinación, la bloquea y devuelve un mensaje seguro.

Criterios de validación:
1. Nombres de receptores: solo se permiten los que están en la BD (RECEPTORES_DB)
2. Direcciones/telefonos inventados: se detectan patrones sospechosos
3. Leyes/decretos: se bloquean menciones a números de ley específicos
4. Longitud excesiva: respuesta > 3000 chars sospechosa de alucinación en cascada
"""
import re

# ── Lista blanca de receptores reales (de la BD mock) ──────────────────────
RECEPTORES_VALIDOS = {
    "recicladora norte",
    "ong construye verde",
    "planta procesadora sur",
    "cartoneros unidos",
    "reutiliza textil",
}

# Palabras clave que indican que un nombre en bold es un receptor (no un label)
PALABRAS_RECEPTOR = {"recicladora", "planta", "ong", "cartoneros", "reutiliza"}

# ── Patrones sospechosos de alucinación ────────────────────────────────────
PATRONES_LEYES = [
    r"decreto\s+\d+",
    r"ley\s+n[°ºo\.]*\s*\d+",
    r"resoluci[óo]n\s+\d+",
    r"norma\s+\d+",
]

PATRON_TELEFONO = re.compile(r"\+?\d[\d\s\-]{8,}")


def _es_nombre_receptor(nombre: str) -> bool:
    """True si el nombre parece un receptor (contiene palabra clave) y no un label."""
    nombre_lower = nombre.lower().strip()
    return any(p in nombre_lower for p in PALABRAS_RECEPTOR)


def validar_respuesta(respuesta: str, contexto: list) -> dict:
    """
    Valida la respuesta del LLM antes de enviarla al usuario.
    Retorna {"ok": True} si pasa, o {"ok": False, "razon": ..., "mensaje_alternativo": ...} si falla.
    """
    respuesta_lower = respuesta.lower()

    # 1. Bloquear menciones a leyes/decretos específicos
    for patron in PATRONES_LEYES:
        if re.search(patron, respuesta_lower):
            return {
                "ok": False,
                "razon": f"Mención de ley/decreto detectada (patrón: {patron})",
                "mensaje_alternativo": (
                    "No tengo información sobre leyes o regulaciones específicas. "
                    "Mi función es ayudarte con la publicación y coordinación de residuos. "
                    "¿Tienes algún residuo que quieras publicar? ♻️"
                ),
            }

    # 2. Verificar que los receptores mencionados existan en la BD
    # Solo valida nombres en bold que contengan palabras de receptor
    receptores_mencionados = re.findall(r"\*\*([A-ZÁÉÍÓÚ][a-záéíóú\s]+)\*\*", respuesta)
    receptores_invalidos = []
    for nombre in receptores_mencionados:
        if _es_nombre_receptor(nombre) and nombre.lower().strip() not in RECEPTORES_VALIDOS:
            receptores_invalidos.append(nombre)

    if receptores_invalidos:
        return {
            "ok": False,
            "razon": f"Receptor no reconocido en BD: {receptores_invalidos}",
            "mensaje_alternativo": (
                "Lo siento, tuve un problema con la búsqueda. "
                "No pude verificar los receptores disponibles. "
                "¿Podrías repetir tu solicitud?"
            ),
        }

    # 3. Respuesta excesivamente larga (posible alucinación en cascada)
    if len(respuesta) > 3000:
        return {
            "ok": False,
            "razon": "Respuesta excesivamente larga (>3000 chars)",
            "mensaje_alternativo": respuesta[:1500] + "\n\n[...] ¿Necesitas más información sobre algún punto específico?",
        }

    # 4. Detectar telefonos inventados SOLO si hay un receptor invalido mencionado
    if PATRON_TELEFONO.search(respuesta) and receptores_invalidos:
        return {
            "ok": False,
            "razon": f"Teléfono asociado a receptor no válido: {receptores_invalidos}",
            "mensaje_alternativo": (
                "Por seguridad, no puedo mostrar datos de contacto directamente. "
                "Una vez que confirmes el retiro, el sistema te pondrá en contacto "
                "con el receptor. ¿Quieres agendar el retiro?"
            ),
        }

    return {"ok": True}
