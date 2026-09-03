"""Guardrail anti-alucinaciones para EcoMatch.

Valida la respuesta del LLM antes de enviarla al usuario.
Bloquea: leyes inventadas, receptores no válidos, respuestas excesivamente largas.
"""
from __future__ import annotations

import re

# Palabras clave que indican que un nombre en bold es un receptor
PALABRAS_RECEPTOR = {"recicladora", "planta", "ong", "cartoneros", "reutiliza"}

PATRONES_LEYES = [
    r"decreto\s+\d+",
    r"ley\s+n[°ºo\.]*\s*\d+",
    r"resoluci[óo]n\s+\d+",
    r"norma\s+\d+",
]

PATRON_TELEFONO = re.compile(r"\+?\d[\d\s\-]{8,}")


def _es_nombre_receptor(nombre: str) -> bool:
    nombre_lower = nombre.lower().strip()
    return any(p in nombre_lower for p in PALABRAS_RECEPTOR)


def validar_respuesta(respuesta: str, receptores_validos: set[str] | None = None) -> dict:
    """
    Valida la respuesta del LLM antes de enviarla al usuario.
    Retorna {"ok": True} si pasa, o {"ok": False, "razon": ..., "mensaje_alternativo": ...} si falla.

    Args:
        respuesta: texto generado por el LLM.
        receptores_validos: set de nombres de receptores en minúscula (de la BD).
    """
    if receptores_validos is None:
        receptores_validos = set()

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
    receptores_mencionados = re.findall(r"\*\*([A-ZÁÉÍÓÚ][a-záéíóú\s]+)\*\*", respuesta)
    receptores_invalidos = []
    for nombre in receptores_mencionados:
        if _es_nombre_receptor(nombre) and nombre.lower().strip() not in receptores_validos:
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

    # 3. Respuesta excesivamente larga
    if len(respuesta) > 3000:
        return {
            "ok": False,
            "razon": "Respuesta excesivamente larga (>3000 chars)",
            "mensaje_alternativo": respuesta[:1500] + "\n\n[...] ¿Necesitas más información sobre algún punto específico?",
        }

    # 4. Teléfonos sospechosos solo si hay receptor inválido
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
