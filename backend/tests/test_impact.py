from __future__ import annotations


def _full_flow(client, auth_headers, collector_user_and_headers, org_user_and_headers):
    org_id, org_headers = org_user_and_headers
    collector_id, collector_headers = collector_user_and_headers

    material = client.post(
        "/api/v1/materials",
        json={"name": "Tablas", "category": "WOOD", "quantity": 20, "unit": "unit", "condition": "REUSABLE", "estimated_weight_kg": 120},
        headers=auth_headers,
    ).json()
    need = client.post(
        "/api/v1/needs",
        json={"material_category": "WOOD", "quantity_required": 15, "unit": "unit", "priority": "HIGH"},
        headers=org_headers,
    ).json()
    matches = client.post(f"/api/v1/matches/generate/{material['id']}", headers=auth_headers).json()
    match_id = matches["matches"][0]["id"]
    client.post(f"/api/v1/matches/{match_id}/accept", headers=auth_headers)
    pickup = client.post("/api/v1/pickups", json={"match_id": match_id, "collector_id": collector_id}, headers=auth_headers).json()
    client.post(f"/api/v1/pickups/{pickup['id']}/accept", headers=collector_headers)
    client.post(f"/api/v1/pickups/{pickup['id']}/start", headers=collector_headers)
    client.post(f"/api/v1/pickups/{pickup['id']}/pickup", headers=collector_headers)
    client.post(f"/api/v1/pickups/{pickup['id']}/deliver", headers=collector_headers)
    return match_id, org_headers


def test_register_impact(client, auth_headers, collector_user_and_headers, org_user_and_headers):
    match_id, org_headers = _full_flow(client, auth_headers, collector_user_and_headers, org_user_and_headers)
    resp = client.post(
        "/api/v1/impact",
        json={"match_id": match_id, "description": "Las tablas fueron usadas para construir tres mesas.", "final_use": "Mobiliario comunitario", "weight_reused_kg": 100, "people_benefited": 30},
        headers=org_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["weight_reused_kg"] == 100
    assert resp.json()["people_benefited"] == 30


def test_impact_stats(client, auth_headers, collector_user_and_headers, org_user_and_headers):
    match_id, org_headers = _full_flow(client, auth_headers, collector_user_and_headers, org_user_and_headers)
    client.post(
        "/api/v1/impact",
        json={"match_id": match_id, "final_use": "Mesas", "weight_reused_kg": 80, "people_benefited": 20},
        headers=org_headers,
    )
    resp = client.get("/api/v1/impact/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_weight_reused_kg"] >= 80
    assert data["total_deliveries"] >= 1
    assert data["organizations_helped"] >= 1
