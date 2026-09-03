from __future__ import annotations

import math

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in kilometers between two points."""
    rlat1, rlat2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def distance_score(distance_km: float | None, max_km: float = 50.0) -> float:
    """Score 0-100, 100 when distance is 0, decreasing linearly to 0 at max_km."""
    if distance_km is None:
        return 50.0
    if distance_km <= 0:
        return 100.0
    if distance_km >= max_km:
        return 0.0
    return max(0.0, 100.0 * (1.0 - distance_km / max_km))
