from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.exceptions import AppException
from app.integrations.osm.geocoding import geocode, reverse_geocode
from app.integrations.osm.routing import calcular_ruta, calcular_ruta_con_geometry

router = APIRouter(prefix="/maps", tags=["Maps"])


class GeocodeRequest(BaseModel):
    direccion: str = Field(..., min_length=3, max_length=300)


class GeocodeResponse(BaseModel):
    lat: float
    lon: float
    display_name: str


class ReverseGeocodeRequest(BaseModel):
    lat: float
    lon: float


class RutaRequest(BaseModel):
    origen_lat: float
    origen_lon: float
    destino_lat: float
    destino_lon: float
    con_geometry: bool = False


class RutaResponse(BaseModel):
    distancia_km: float
    duracion_min: float
    geometry: list | None = None


@router.post("/geocode", response_model=GeocodeResponse)
async def geocode_endpoint(req: GeocodeRequest):
    result = await geocode(req.direccion)
    if not result:
        raise AppException(404, "GEOCODE_NOT_FOUND", "Dirección no encontrada")
    return result


@router.post("/reverse-geocode", response_model=GeocodeResponse)
async def reverse_geocode_endpoint(req: ReverseGeocodeRequest):
    result = await reverse_geocode(req.lat, req.lon)
    if not result:
        raise AppException(404, "REVERSE_NOT_FOUND", "Ubicación no encontrada")
    return result


@router.post("/ruta", response_model=RutaResponse)
async def ruta_endpoint(req: RutaRequest):
    origen = {"lat": req.origen_lat, "lon": req.origen_lon}
    destino = {"lat": req.destino_lat, "lon": req.destino_lon}
    if req.con_geometry:
        result = await calcular_ruta_con_geometry(origen, destino)
    else:
        result = await calcular_ruta(origen, destino)
    if not result:
        raise AppException(404, "ROUTE_NOT_FOUND", "No se pudo calcular la ruta")
    return result
