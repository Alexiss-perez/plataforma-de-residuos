"""Security audit tests — verify auth and authorization on all endpoints."""
from __future__ import annotations


def test_materials_require_auth(client):
    resp = client.get("/api/v1/materials")
    assert resp.status_code == 401


def test_material_by_id_requires_auth(client):
    resp = client.get("/api/v1/materials/1")
    assert resp.status_code == 401


def test_matches_by_material_require_auth(client):
    resp = client.get("/api/v1/matches/material/1")
    assert resp.status_code == 401


def test_matches_by_need_require_auth(client):
    resp = client.get("/api/v1/matches/need/1")
    assert resp.status_code == 401


def test_organizations_require_auth(client):
    resp = client.get("/api/v1/organizations")
    assert resp.status_code == 401


def test_projects_require_auth(client):
    resp = client.get("/api/v1/projects")
    assert resp.status_code == 401


def test_needs_require_auth(client):
    resp = client.get("/api/v1/needs")
    assert resp.status_code == 401


def test_impact_require_auth(client):
    resp = client.get("/api/v1/impact")
    assert resp.status_code == 401


def test_impact_stats_require_auth(client):
    resp = client.get("/api/v1/impact/stats")
    assert resp.status_code == 401


def test_match_accept_by_unrelated_user_forbidden(client, auth_headers, org_user_and_headers):
    _, org_headers = org_user_and_headers
    material = client.post(
        "/api/v1/materials",
        json={"name": "wood", "category": "WOOD", "quantity": 10, "unit": "unit", "condition": "GOOD"},
        headers=auth_headers,
    ).json()
    client.post(
        "/api/v1/needs",
        json={"material_category": "WOOD", "quantity_required": 5, "unit": "unit", "priority": "HIGH"},
        headers=org_headers,
    )
    matches = client.post(f"/api/v1/matches/generate/{material['id']}", headers=auth_headers).json()
    match_id = matches["matches"][0]["id"]

    other = client.post("/api/v1/auth/register", json={"name": "X", "email": "x@sec.cl", "password": "pass12345"})
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    resp = client.post(f"/api/v1/matches/{match_id}/accept", headers=other_headers)
    assert resp.status_code == 403


def test_pickup_address_hidden_for_non_participant(client, auth_headers, collector_user_and_headers, org_user_and_headers):
    _, org_headers = org_user_and_headers
    collector_id, collector_headers = collector_user_and_headers

    material = client.post(
        "/api/v1/materials",
        json={"name": "wood", "category": "WOOD", "quantity": 10, "unit": "unit", "condition": "GOOD"},
        headers=auth_headers,
    ).json()
    client.post(
        "/api/v1/needs",
        json={"material_category": "WOOD", "quantity_required": 5, "unit": "unit", "priority": "HIGH"},
        headers=org_headers,
    )
    matches = client.post(f"/api/v1/matches/generate/{material['id']}", headers=auth_headers).json()
    match_id = matches["matches"][0]["id"]
    client.post(f"/api/v1/matches/{match_id}/accept", headers=auth_headers)
    pickup = client.post(
        "/api/v1/pickups",
        json={"match_id": match_id, "collector_id": collector_id, "pickup_address": "SECRET", "delivery_address": "SECRET2"},
        headers=auth_headers,
    ).json()

    stranger = client.post("/api/v1/auth/register", json={"name": "S", "email": "s@sec.cl", "password": "pass12345"})
    stranger_headers = {"Authorization": f"Bearer {stranger.json()['access_token']}"}

    resp = client.get(f"/api/v1/pickups/{pickup['id']}", headers=stranger_headers)
    assert resp.status_code == 403


def test_pickup_visible_to_donor(client, auth_headers, collector_user_and_headers, org_user_and_headers):
    _, org_headers = org_user_and_headers
    collector_id, collector_headers = collector_user_and_headers

    material = client.post(
        "/api/v1/materials",
        json={"name": "wood", "category": "WOOD", "quantity": 10, "unit": "unit", "condition": "GOOD"},
        headers=auth_headers,
    ).json()
    client.post(
        "/api/v1/needs",
        json={"material_category": "WOOD", "quantity_required": 5, "unit": "unit", "priority": "HIGH"},
        headers=org_headers,
    )
    matches = client.post(f"/api/v1/matches/generate/{material['id']}", headers=auth_headers).json()
    match_id = matches["matches"][0]["id"]
    client.post(f"/api/v1/matches/{match_id}/accept", headers=auth_headers)
    pickup = client.post(
        "/api/v1/pickups",
        json={"match_id": match_id, "collector_id": collector_id, "pickup_address": "my addr"},
        headers=auth_headers,
    ).json()

    resp = client.get(f"/api/v1/pickups/{pickup['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["pickup_address"] == "my addr"


def test_match_reject_by_unrelated_user_forbidden(client, auth_headers, org_user_and_headers):
    _, org_headers = org_user_and_headers
    material = client.post(
        "/api/v1/materials",
        json={"name": "wood", "category": "WOOD", "quantity": 10, "unit": "unit", "condition": "GOOD"},
        headers=auth_headers,
    ).json()
    client.post(
        "/api/v1/needs",
        json={"material_category": "WOOD", "quantity_required": 5, "unit": "unit", "priority": "HIGH"},
        headers=org_headers,
    )
    matches = client.post(f"/api/v1/matches/generate/{material['id']}", headers=auth_headers).json()
    match_id = matches["matches"][0]["id"]

    other = client.post("/api/v1/auth/register", json={"name": "Y", "email": "y@sec.cl", "password": "pass12345"})
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    resp = client.post(f"/api/v1/matches/{match_id}/reject", headers=other_headers)
    assert resp.status_code == 403
