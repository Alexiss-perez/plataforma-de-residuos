from __future__ import annotations

from app.services.matching_service import compute_match
from app.models.models import Material, Need, Organization, User
from app.models.enums import (
    MaterialCategoryEnum,
    MaterialConditionEnum,
    NeedPriorityEnum,
    RoleEnum,
)


def _make_material(category="WOOD", quantity=20, condition="REUSABLE", lat=-33.45, lon=-70.66):
    owner = User(id=1, name="Owner", email="owner@test.cl", password_hash="x", role=RoleEnum.NATURAL, latitude=lat, longitude=lon)
    m = Material(id=1, owner_id=1, name="test", category=category, quantity=quantity, unit="unit", condition=condition, risk_level="SAFE", requires_pickup=True, status="AVAILABLE", estimated_weight_kg=10)
    m.owner = owner
    return m


def _make_need(category="WOOD", qty=15, priority="HIGH", lat=-33.45, lon=-70.66):
    org = Organization(id=1, owner_id=2, name="Org", type="NGO", verified=True)
    org.latitude = lat
    org.longitude = lon
    need = Need(id=1, organization_id=1, material_category=category, quantity_required=qty, quantity_received=0, unit="unit", priority=priority, status="OPEN")
    need.organization = org
    return need


def test_match_compatible_high_score():
    m = _make_material("WOOD", 20, "REUSABLE")
    n = _make_need("WOOD", 15, "HIGH")
    scores = compute_match(m, n)
    assert scores["material_score"] == 100
    assert scores["quantity_score"] == 100
    assert scores["score"] > 80


def test_match_incompatible_category():
    m = _make_material("WOOD", 20, "GOOD")
    n = _make_need("METAL", 15, "HIGH")
    scores = compute_match(m, n)
    assert scores["material_score"] == 0
    assert scores["score"] < 60


def test_match_quantity_partial():
    m = _make_material("WOOD", 5, "GOOD")
    n = _make_need("WOOD", 20, "HIGH")
    scores = compute_match(m, n)
    assert scores["quantity_score"] == 25.0


def test_match_distance_far():
    m = _make_material("WOOD", 20, "GOOD", lat=-33.45, lon=-70.66)
    n = _make_need("WOOD", 20, "HIGH", lat=-34.0, lon=-71.0)
    scores = compute_match(m, n)
    assert scores["distance_score"] < 50


def test_match_distance_close():
    m = _make_material("WOOD", 20, "GOOD", lat=-33.45, lon=-70.66)
    n = _make_need("WOOD", 20, "HIGH", lat=-33.4501, lon=-70.6601)
    scores = compute_match(m, n)
    assert scores["distance_score"] > 95


def test_match_priority_urgent():
    m = _make_material("WOOD", 20, "GOOD")
    n = _make_need("WOOD", 20, "URGENT")
    scores = compute_match(m, n)
    assert scores["priority_score"] == 100


def test_match_condition_new_best():
    m = _make_material("WOOD", 20, "NEW")
    n = _make_need("WOOD", 20, "HIGH")
    scores = compute_match(m, n)
    assert scores["condition_score"] == 100


def test_generate_hazardous_blocked(client, auth_headers):
    resp = client.post(
        "/api/v1/materials",
        json={"name": "Asbestos sheet", "category": "OTHER", "quantity": 1, "unit": "unit", "condition": "UNKNOWN", "description": "contains asbestos"},
        headers=auth_headers,
    )
    mat_id = resp.json()["id"]
    resp2 = client.post(f"/api/v1/matches/generate/{mat_id}", headers=auth_headers)
    assert resp2.status_code == 422
    assert resp2.json()["error"]["code"] == "HAZARDOUS_MATERIAL"
