from __future__ import annotations

import httpx

from app.integrations.osm.config import osm_settings


async def calcular_ruta(origen: dict, destino: dict) -> dict | None:
    """
    Calcula distancia y duración de ruta entre dos puntos.
    Usa OSRM (OpenStreetMap Routing Machine). Gratis.
    """
    coords = f"{origen['lon']},{origen['lat']};{destino['lon']},{destino['lat']}"
    async with httpx.AsyncClient(timeout=osm_settings.OSM_TIMEOUT) as client:
        r = await client.get(
            f"{osm_settings.OSRM_URL}/{coords}",
            params={"overview": "false"},
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != "Ok":
            return None
        route = data["routes"][0]
        return {
            "distancia_km": round(route["distance"] / 1000, 2),
            "duracion_min": round(route["duration"] / 60, 1),
        }


async def calcular_ruta_con_geometry(origen: dict, destino: dict) -> dict | None:
    """
    Igual que calcular_ruta pero incluye la polilínea para dibujar en el mapa.
    """
    coords = f"{origen['lon']},{origen['lat']};{destino['lon']},{destino['lat']}"
    async with httpx.AsyncClient(timeout=osm_settings.OSM_TIMEOUT) as client:
        r = await client.get(
            f"{osm_settings.OSRM_URL}/{coords}",
            params={"overview": "full", "geometries": "geojson"},
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != "Ok":
            return None
        route = data["routes"][0]
        return {
            "distancia_km": round(route["distance"] / 1000, 2),
            "duracion_min": round(route["duration"] / 60, 1),
            "geometry": route["geometry"]["coordinates"],
        }
