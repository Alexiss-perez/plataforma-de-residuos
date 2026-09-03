from __future__ import annotations

import httpx

from app.integrations.osm.config import osm_settings


async def geocode(direccion: str) -> dict | None:
    """
    Convierte una dirección textual en coordenadas lat/lon.
    Usa Nominatim (OpenStreetMap). Gratis, sin API key.
    Límite: 1 request/segundo.
    """
    headers = {"User-Agent": osm_settings.OSM_USER_AGENT}
    async with httpx.AsyncClient(timeout=osm_settings.OSM_TIMEOUT) as client:
        r = await client.get(
            osm_settings.NOMINATIM_URL,
            params={
                "q": direccion,
                "format": "json",
                "limit": 1,
                "countrycodes": "cl",
            },
            headers=headers,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return {
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"]),
            "display_name": data[0]["display_name"],
        }


async def reverse_geocode(lat: float, lon: float) -> dict | None:
    """
    Coordenadas -> dirección textual (reverse geocoding).
    """
    headers = {"User-Agent": osm_settings.OSM_USER_AGENT}
    async with httpx.AsyncClient(timeout=osm_settings.OSM_TIMEOUT) as client:
        r = await client.get(
            osm_settings.NOMINATIM_REVERSE_URL,
            params={
                "lat": lat,
                "lon": lon,
                "format": "json",
            },
            headers=headers,
        )
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            return None
        return {
            "lat": float(data["lat"]),
            "lon": float(data["lon"]),
            "display_name": data["display_name"],
        }
