from __future__ import annotations

from app.utils.distance import haversine_km, distance_score
from app.utils.hazardous import is_hazardous, determine_risk_level


def test_haversine_zero():
    assert haversine_km(-33.45, -70.66, -33.45, -70.66) == 0.0


def test_haversine_known_distance():
    d = haversine_km(-33.45, -70.66, -33.46, -70.66)
    assert 1.0 < d < 1.2


def test_distance_score_zero_km():
    assert distance_score(0) == 100.0


def test_distance_score_far():
    assert distance_score(100) == 0.0


def test_is_hazardous_asbestos():
    assert is_hazardous("OTHER", "panel con asbesto")


def test_is_hazardous_safe():
    assert not is_hazardous("WOOD", "tablas de pino")


def test_determine_risk_level_hazardous():
    assert determine_risk_level("OTHER", "aceite contaminado") == "SPECIAL_HANDLING"


def test_determine_risk_level_safe():
    assert determine_risk_level("WOOD", "tablas") == "SAFE"
