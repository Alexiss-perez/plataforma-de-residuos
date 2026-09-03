"""
Implementaciones de las herramientas del agente EcoMatch.

- buscar_receptores / crear_oferta / agendar_retiro: MOCK (Backend las reemplaza)
- calcular_distancia: API real de OpenStreetMap Nominatim (gratis, sin API key)
- obtener_historial: MOCK

Regla CRÍTICA: Ninguna función inventa datos aleatorios. Todas devuelven datos
reales o predefinidos determinísticos, para que el agente NUNCA alucine.
"""
import json
import urllib.request
import urllib.parse
from datetime import datetime

# ── Base de datos mock de receptores ────────────────────────────────────────
# Simula la tabla Receptor de la BD real. El Backend conectará esto a PostgreSQL.
RECEPTORES_DB = [
    {
        "id": 1,
        "nombre": "Recicladora Norte",
        "tipo": "planta_reciclaje",
        "materiales_aceptados": ["escombros", "metal", "plastico"],
        "direccion": "Av. Norte 450",
        "telefono": "+56 2 2345 6789",
        "capacidad_disponible": "50 toneladas/semana",
    },
    {
        "id": 2,
        "nombre": "ONG Construye Verde",
        "tipo": "ong",
        "materiales_aceptados": ["madera", "escombros", "metal"],
        "direccion": "Calle Verde 12",
        "telefono": "+56 9 8765 4321",
        "capacidad_disponible": "20 toneladas/semana",
    },
    {
        "id": 3,
        "nombre": "Planta Procesadora Sur",
        "tipo": "planta_reciclaje",
        "materiales_aceptados": ["escombros", "vidrio", "plastico"],
        "direccion": "Av. Sur 890",
        "telefono": "+56 2 2233 4455",
        "capacidad_disponible": "100 toneladas/semana",
    },
    {
        "id": 4,
        "nombre": "Cartoneros Unidos",
        "tipo": "pyme",
        "materiales_aceptados": ["carton", "plastico"],
        "direccion": "Pasaje Reciclaje 7",
        "telefono": "+56 9 1122 3344",
        "capacidad_disponible": "5 toneladas/semana",
    },
    {
        "id": 5,
        "nombre": "Reutiliza Textil",
        "tipo": "ong",
        "materiales_aceptados": ["textil", "madera"],
        "direccion": "Calle Tela 99",
        "telefono": "+56 9 5566 7788",
        "capacidad_disponible": "2 toneladas/semana",
    },
]

# ── Contador en memoria para IDs de ofertas ─────────────────────────────────
_ofertas_db = []
_retiro_db = []
_next_oferta_id = 1
_next_retiro_id = 1


# ── Implementaciones ────────────────────────────────────────────────────────
def buscar_receptores_impl(material: str, radio_km: float, ubicacion: str) -> dict:
    """
    Busca receptores que acepten el material indicado.
    Filtra por material aceptado. El radio_km se simula (en producción se usa PostGIS).
    """
    receptores_encontrados = [
        {
            "id": r["id"],
            "nombre": r["nombre"],
            "tipo": r["tipo"],
            "direccion": r["direccion"],
            "distancia_km": round(2.5 + i * 3.3, 1),  # distancia simulada determinística
            "capacidad_disponible": r["capacidad_disponible"],
        }
        for i, r in enumerate(RECEPTORES_DB)
        if material.lower() in r["materiales_aceptados"]
    ]

    return {
        "total": len(receptores_encontrados),
        "material_buscado": material,
        "radio_km": radio_km,
        "receptores": receptores_encontrados,
    }


def crear_oferta_residuo_impl(
    material: str,
    volumen: str,
    ubicacion: str,
    tipo_generador: str,
    notas: str = "",
) -> dict:
    """Registra la oferta en la BD mock y devuelve el ID asignado."""
    global _next_oferta_id

    oferta = {
        "id": _next_oferta_id,
        "material": material,
        "volumen": volumen,
        "ubicacion": ubicacion,
        "tipo_generador": tipo_generador,
        "notas": notas,
        "estado": "publicada",
        "fecha_creacion": datetime.now().isoformat(),
    }
    _ofertas_db.append(oferta)
    _next_oferta_id += 1

    return {"status": "ok", "oferta_id": oferta["id"], "mensaje": "Oferta registrada correctamente."}


def agendar_retiro_impl(
    receptor_id: int,
    oferta_id: int,
    fecha: str,
    hora: str,
) -> dict:
    """Agenda el retiro entre generador y receptor."""
    global _next_retiro_id

    receptor = next((r for r in RECEPTORES_DB if r["id"] == receptor_id), None)
    if not receptor:
        return {"error": f"No existe receptor con id={receptor_id}"}

    oferta = next((o for o in _ofertas_db if o["id"] == oferta_id), None)
    if not oferta:
        return {"error": f"No existe oferta con id={oferta_id}"}

    retiro = {
        "id": _next_retiro_id,
        "receptor": receptor["nombre"],
        "material": oferta["material"],
        "volumen": oferta["volumen"],
        "origen": oferta["ubicacion"],
        "destino": receptor["direccion"],
        "fecha": fecha,
        "hora": hora,
        "estado": "agendado",
    }
    _retiro_db.append(retiro)
    _next_retiro_id += 1

    return {"status": "ok", "retiro_id": retiro["id"], "detalle": retiro}


def calcular_distancia_impl(origen: str, destino: str) -> dict:
    """
    Calcula la distancia real entre dos direcciones usando OpenStreetMap Nominatim (gratis).
    Si la API falla, devuelve un error explícito (NUNCA inventa una distancia).
    """
    try:
        def geocodificar(direccion: str) -> tuple[float, float] | None:
            url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
                "q": direccion,
                "format": "json",
                "limit": 1,
            })
            req = urllib.request.Request(url, headers={"User-Agent": "EcoMatch/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            if not data:
                return None
            return float(data[0]["lat"]), float(data[0]["lon"])

        coords_origen = geocodificar(origen)
        coords_destino = geocodificar(destino)

        if not coords_origen or not coords_destino:
            return {
                "origen": origen,
                "destino": destino,
                "error": "No se pudo geocodificar una de las direcciones. Verifica que sean direcciones reales.",
            }

        # Fórmula de Haversine para distancia entre dos puntos GPS
        import math
        lat1, lon1 = coords_origen
        lat2, lon2 = coords_destino
        R = 6371  # radio de la Tierra en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        distancia_km = round(R * c, 2)

        return {
            "origen": origen,
            "destino": destino,
            "distancia_km": distancia_km,
            "duracion_estimada_min": int(distancia_km * 3),
            "coords_origen": coords_origen,
            "coords_destino": coords_destino,
        }
    except Exception as e:
        return {
            "origen": origen,
            "destino": destino,
            "error": f"No se pudo calcular la distancia: {e}",
        }


def obtener_historial_usuario_impl(user_id: int) -> dict:
    """Devuelve el historial de ofertas del usuario."""
    return {
        "user_id": user_id,
        "total_ofertas": len(_ofertas_db),
        "ofertas": _ofertas_db,
        "total_retiros": len(_retiro_db),
        "retiros": _retiro_db,
    }
