from __future__ import annotations


def test_create_material(client, auth_headers):
    resp = client.post(
        "/api/v1/materials",
        json={"name": "Tablas", "category": "WOOD", "quantity": 10, "unit": "unit", "condition": "GOOD"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Tablas"
    assert data["category"] == "WOOD"
    assert data["status"] == "AVAILABLE"


def test_list_materials(client, auth_headers):
    client.post("/api/v1/materials", json={"name": "Madera", "category": "WOOD", "quantity": 5, "unit": "unit", "condition": "GOOD"}, headers=auth_headers)
    resp = client.get("/api/v1/materials", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_material_status_default(client, auth_headers):
    resp = client.post("/api/v1/materials", json={"name": "Silla", "category": "FURNITURE", "quantity": 1, "unit": "unit", "condition": "NEW"}, headers=auth_headers)
    assert resp.json()["status"] == "AVAILABLE"


def test_hazardous_auto_detected(client, auth_headers):
    resp = client.post(
        "/api/v1/materials",
        json={"name": "Asbestos", "category": "OTHER", "quantity": 1, "unit": "unit", "condition": "UNKNOWN", "description": "material con asbesto"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["risk_level"] == "SPECIAL_HANDLING"
