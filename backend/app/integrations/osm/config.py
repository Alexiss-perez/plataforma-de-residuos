from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class OSMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org/search"
    NOMINATIM_REVERSE_URL: str = "https://nominatim.openstreetmap.org/reverse"
    OSRM_URL: str = "http://router.project-osrm.org/route/v1/driving"
    DEFAULT_SEARCH_RADIUS_KM: float = 10.0
    OSM_USER_AGENT: str = "ReVinculo/1.0"
    OSM_TIMEOUT: float = 10.0


@lru_cache
def get_osm_settings() -> OSMSettings:
    return OSMSettings()


osm_settings = get_osm_settings()
