"""
Implementaciones de las herramientas del agente EcoMatch.
Conectadas a Supabase (PostgreSQL) real.

- buscar_receptores:       Query a tabla receptores en Supabase
- crear_oferta_residuo:    Insert en tabla ofertas_residuo
- agendar_retiro:          Insert en tabla retiros
- calcular_distancia:      API real de OpenStreetMap Nominatim (gratis)
- obtener_historial:       Query a ofertas_residuo + retiros del usuario

Requiere:
    pip install supabase
    export SUPABASE_URL="https://tgxseiaqebedzlgnutmm.supabase.co"
    export SUPABASE_KEY="sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8"
"""
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

from supabase import create_client

# ── Cliente Supabase ────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "https://tgxseiaqebedzlgnutmm.supabase.co",
)
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "sb_publishable_geOVgQQ-s_NwXd-PJMZKxg_8wrFoAt8",
)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ── Implementaciones ────────────────────────────────────────────────────────
def buscar_receptores_impl(material: str, radio_km: float, ubicacion: str) -> dict:
    """
    Busca receptores en Supabase que acepten el material indicado.
    Filtra por material dentro del array materiales_aceptados.
    """
    response = supabase.table("receptores").select(
        "id, nombre, tipo, direccion, capacidad_disponible, materiales_aceptados"
    ).contains("materiales_aceptados", [material]).execute()

    receptores = []
    for i, r in enumerate(response.data):
        receptores.append({
            "id": r["id"],
            "nombre": r["nombre"],
            "tipo": r["tipo"],
            "direccion": r["direccion"],
            "distancia_km": round(2.5 + i * 3.3, 1),  # TODO: reemplazar con PostGIS o calcular_distancia
            "capacidad_disponible": r["capacidad_disponible"],
        })

    return {
        "total": len(receptores),
        "material_buscado": material,
        "radio_km": radio_km,
        "receptores": receptores,
    }


def crear_oferta_residuo_impl(
    material: str,
    volumen: str,
    ubicacion: str,
    tipo_generador: str,
    notas: str = "",
) -> dict:
    """Registra la oferta en Supabase (tabla ofertas_residuo)."""
    # TODO: el usuario_id debe venir del JWT del frontend.
    # Por ahora usamos un usuario de prueba si existe, o None.
    usuario_id = os.environ.get("ECOMATCH_USER_ID", None)

    oferta_data = {
        "material": material,
        "volumen": volumen,
        "ubicacion": ubicacion,
        "tipo_generador": tipo_generador,
        "notas": notas,
        "estado": "publicada",
    }
    if usuario_id:
        oferta_data["usuario_id"] = usuario_id

    response = supabase.table("ofertas_residuo").insert(oferta_data).execute()

    if response.data:
        return {
            "status": "ok",
            "oferta_id": response.data[0]["id"],
            "mensaje": "Oferta registrada correctamente en Supabase.",
        }
    return {"error": "No se pudo registrar la oferta."}


def agendar_retiro_impl(
    receptor_id: int,
    oferta_id: str,
    fecha: str,
    hora: str,
) -> dict:
    """Agenda el retiro en Supabase (tabla retiros)."""
    retiro_data = {
        "oferta_id": oferta_id,
        "receptor_id": receptor_id,
        "fecha": fecha,
        "hora": hora,
        "estado": "agendado",
    }

    response = supabase.table("retiros").insert(retiro_data).execute()

    if not response.data:
        return {"error": "No se pudo agendar el retiro."}

    retiro = response.data[0]

    # Obtener detalles de la oferta y receptor para el resumen
    oferta_resp = supabase.table("ofertas_residuo").select("*").eq("id", oferta_id).execute()
    receptor_resp = supabase.table("receptores").select("nombre, direccion").eq("id", receptor_id).execute()

    detalle = {
        "id": retiro["id"],
        "receptor": receptor_resp.data[0]["nombre"] if receptor_resp.data else "Desconocido",
        "material": oferta_resp.data[0]["material"] if oferta_resp.data else "Desconocido",
        "volumen": oferta_resp.data[0]["volumen"] if oferta_resp.data else "Desconocido",
        "origen": oferta_resp.data[0]["ubicacion"] if oferta_resp.data else "Desconocido",
        "destino": receptor_resp.data[0]["direccion"] if receptor_resp.data else "Desconocido",
        "fecha": fecha,
        "hora": hora,
        "estado": "agendado",
    }

    return {"status": "ok", "retiro_id": retiro["id"], "detalle": detalle}


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

        import math
        lat1, lon1 = coords_origen
        lat2, lon2 = coords_destino
        R = 6371
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


def obtener_historial_usuario_impl(user_id: str) -> dict:
    """Devuelve el historial de ofertas y retiros del usuario desde Supabase."""
    ofertas_resp = supabase.table("ofertas_residuo").select("*").eq("usuario_id", user_id).execute()

    retiros_resp = supabase.rpc(
        "get_user_retiros", {"p_user_id": user_id}
    ).execute()

    return {
        "user_id": user_id,
        "total_ofertas": len(ofertas_resp.data),
        "ofertas": ofertas_resp.data,
        "total_retiros": len(retiros_resp.data) if retiros_resp.data else 0,
        "retiros": retiros_resp.data if retiros_resp.data else [],
    }
