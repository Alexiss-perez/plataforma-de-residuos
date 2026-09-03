from __future__ import annotations


def _setup_match(client, auth_headers, org_headers):
    material = client.post(
        "/api/v1/materials",
        json={"name": "Tablas de madera", "category": "WOOD", "quantity": 20, "unit": "unit", "condition": "REUSABLE", "estimated_weight_kg": 120},
        headers=auth_headers,
    ).json()
    need = client.post(
        "/api/v1/needs",
        json={"material_category": "WOOD", "material_name": "Tablas", "quantity_required": 15, "unit": "unit", "priority": "HIGH"},
        headers=org_headers,
    ).json()
    matches = client.post(f"/api/v1/matches/generate/{material['id']}", headers=auth_headers).json()
    assert len(matches["matches"]) >= 1
    match_id = matches["matches"][0]["id"]
    return material, need, match_id


def test_pickup_full_flow(client, auth_headers, collector_user_and_headers, org_user_and_headers):
    org_id, org_headers = org_user_and_headers
    collector_id, collector_headers = collector_user_and_headers

    material, need, match_id = _setup_match(client, auth_headers, org_headers)

    accept_resp = client.post(f"/api/v1/matches/{match_id}/accept", headers=auth_headers)
    assert accept_resp.status_code == 200

    pickup = client.post(
        "/api/v1/pickups",
        json={"match_id": match_id, "collector_id": collector_id, "pickup_address": "Calle 1", "delivery_address": "Calle 2"},
        headers=auth_headers,
    )
    assert pickup.status_code == 201
    pickup_id = pickup.json()["id"]
    assert pickup.json()["status"] == "ASSIGNED"

    accept = client.post(f"/api/v1/pickups/{pickup_id}/accept", headers=collector_headers)
    assert accept.status_code == 200
    assert accept.json()["status"] == "ACCEPTED"

    start = client.post(f"/api/v1/pickups/{pickup_id}/start", headers=collector_headers)
    assert start.json()["status"] == "ON_ROUTE"

    picked = client.post(f"/api/v1/pickups/{pickup_id}/pickup", headers=collector_headers)
    assert picked.json()["status"] == "PICKED_UP"

    delivered = client.post(f"/api/v1/pickups/{pickup_id}/deliver", headers=collector_headers)
    assert delivered.json()["status"] == "DELIVERED"


def test_illegal_transition_pending_to_delivered(client, auth_headers, collector_user_and_headers, org_user_and_headers):
    org_id, org_headers = org_user_and_headers
    collector_id, collector_headers = collector_user_and_headers

    material, need, match_id = _setup_match(client, auth_headers, org_headers)
    client.post(f"/api/v1/matches/{match_id}/accept", headers=auth_headers)
    pickup = client.post(
        "/api/v1/pickups",
        json={"match_id": match_id, "collector_id": collector_id},
        headers=auth_headers,
    )
    pickup_id = pickup.json()["id"]

    deliver = client.post(f"/api/v1/pickups/{pickup_id}/deliver", headers=collector_headers)
    assert deliver.status_code == 409
    assert deliver.json()["error"]["code"] == "ILLEGAL_TRANSITION"


def test_pickup_cancel_and_replacement(client, auth_headers, collector_user_and_headers, org_user_and_headers):
    org_id, org_headers = org_user_and_headers
    collector_id, collector_headers = collector_user_and_headers

    second_collector = client.post(
        "/api/v1/auth/register",
        json={"name": "Collector 2", "email": "col2@example.com", "password": "pass12345", "role": "COLLECTOR", "can_collect": True, "commune": "Santiago", "latitude": -33.46, "longitude": -70.65},
    )
    sc_id = second_collector.json()["user"]["id"]
    sc_token = second_collector.json()["access_token"]
    sc_headers = {"Authorization": f"Bearer {sc_token}"}
    client.post(
        "/api/v1/collectors/profile",
        json={"vehicle_type": "Camioneta", "max_weight_kg": 400, "radius_km": 30, "available": True, "materials_accepted": ["WOOD"]},
        headers=sc_headers,
    )

    material, need, match_id = _setup_match(client, auth_headers, org_headers)
    client.post(f"/api/v1/matches/{match_id}/accept", headers=auth_headers)
    pickup = client.post("/api/v1/pickups", json={"match_id": match_id, "collector_id": collector_id}, headers=auth_headers)
    pickup_id = pickup.json()["id"]

    cancel = client.post(f"/api/v1/pickups/{pickup_id}/cancel", headers=collector_headers)
    assert cancel.json()["status"] == "CANCELLED"

    replacements = client.get(f"/api/v1/pickups/{pickup_id}/replacements", headers=auth_headers)
    assert replacements.status_code == 200
    assert isinstance(replacements.json(), list)
