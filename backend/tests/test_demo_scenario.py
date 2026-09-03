"""End-to-end demo scenario test — the full 15-step flow from the spec."""
from __future__ import annotations


def test_full_demo_scenario(client):
    # PASO 1: Usuario se registra
    donor = client.post(
        "/api/v1/auth/register",
        json={
            "name": "María González",
            "email": "maria@demo.cl",
            "password": "pass12345",
            "commune": "Providencia",
            "latitude": -33.45,
            "longitude": -70.66,
        },
    )
    assert donor.status_code == 201
    donor_headers = {"Authorization": f"Bearer {donor.json()['access_token']}"}

    # PASO 2: Publica "20 tablas de madera"
    post = client.post(
        "/api/v1/posts",
        json={"type": "OFFER", "title": "Terminé una remodelación y tengo 20 tablas de madera", "commune": "Providencia", "latitude": -33.45, "longitude": -70.66},
        headers=donor_headers,
    )
    assert post.status_code == 201

    material = client.post(
        "/api/v1/materials",
        json={"post_id": post.json()["id"], "name": "20 tablas de madera", "category": "WOOD", "quantity": 20, "unit": "unit", "condition": "REUSABLE", "estimated_weight_kg": 120},
        headers=donor_headers,
    )
    assert material.status_code == 201
    material_id = material.json()["id"]

    # PASO 3: EcoMatchAgent clasifica (mock)
    analysis = client.post(
        "/api/v1/ai/analyze-material",
        json={"message": "Tengo 20 tablas de madera después de una remodelación"},
        headers=donor_headers,
    )
    assert analysis.status_code == 200

    # PASO 4: Fundación Construyendo Juntos + proyecto + necesidad
    org_user = client.post(
        "/api/v1/auth/register",
        json={"name": "Fundación", "email": "fundacion@demo.cl", "password": "pass12345", "role": "ORGANIZATION", "commune": "Providencia", "latitude": -33.4501, "longitude": -70.6601},
    )
    org_headers = {"Authorization": f"Bearer {org_user.json()['access_token']}"}
    org = client.post(
        "/api/v1/organizations",
        json={"name": "Fundación Construyendo Juntos", "type": "FOUNDATION", "commune": "Providencia", "latitude": -33.4501, "longitude": -70.6601},
        headers=org_headers,
    )
    assert org.status_code == 201

    project = client.post(
        "/api/v1/projects",
        json={"title": "Mobiliario comunitario", "description": "Mesas para sede social", "commune": "Providencia"},
        headers=org_headers,
    )
    assert project.status_code == 201

    need = client.post(
        "/api/v1/needs",
        json={"project_id": project.json()["id"], "material_category": "WOOD", "material_name": "tablas", "quantity_required": 15, "unit": "unit", "priority": "HIGH"},
        headers=org_headers,
    )
    assert need.status_code == 201

    # PASO 5: Matching genera alta compatibilidad
    matches = client.post(f"/api/v1/matches/generate/{material_id}", headers=donor_headers)
    assert matches.status_code == 200
    assert len(matches.json()["matches"]) >= 1
    best_match = matches.json()["matches"][0]
    assert best_match["score"] > 70, f"Expected high score, got {best_match['score']}"
    match_id = best_match["id"]

    # PASO 6: Se acepta match
    accept = client.post(f"/api/v1/matches/{match_id}/accept", headers=donor_headers)
    assert accept.status_code == 200
    assert accept.json()["status"] == "ACCEPTED"

    # PASO 7: Sistema encuentra recolector con camioneta
    collector = client.post(
        "/api/v1/auth/register",
        json={"name": "Jorge", "email": "jorge@demo.cl", "password": "pass12345", "role": "COLLECTOR", "can_collect": True, "commune": "Santiago", "latitude": -33.44, "longitude": -70.65},
    )
    collector_headers = {"Authorization": f"Bearer {collector.json()['access_token']}"}
    collector_id = collector.json()["user"]["id"]
    cp = client.post(
        "/api/v1/collectors/profile",
        json={"vehicle_type": "Camioneta", "max_weight_kg": 500, "radius_km": 30, "available": True, "materials_accepted": ["WOOD"]},
        headers=collector_headers,
    )
    assert cp.status_code == 201

    # PASO 8: Se crea retiro
    pickup = client.post(
        "/api/v1/pickups",
        json={"match_id": match_id, "collector_id": collector_id, "pickup_address": "Calle Privada 123", "delivery_address": "Sede Social 456"},
        headers=donor_headers,
    )
    assert pickup.status_code == 201
    pickup_id = pickup.json()["id"]

    # PASO 9: Recolector acepta
    r = client.post(f"/api/v1/pickups/{pickup_id}/accept", headers=collector_headers)
    assert r.json()["status"] == "ACCEPTED"

    # PASO 10: Simular cancelación
    r = client.post(f"/api/v1/pickups/{pickup_id}/cancel", headers=collector_headers)
    assert r.json()["status"] == "CANCELLED"

    # PASO 11: Sistema encuentra otro recolector compatible
    collector2 = client.post(
        "/api/v1/auth/register",
        json={"name": "Felipe", "email": "felipe@demo.cl", "password": "pass12345", "role": "COLLECTOR", "can_collect": True, "commune": "Santiago", "latitude": -33.46, "longitude": -70.65},
    )
    c2_headers = {"Authorization": f"Bearer {collector2.json()['access_token']}"}
    c2_id = collector2.json()["user"]["id"]
    client.post(
        "/api/v1/collectors/profile",
        json={"vehicle_type": "Camioneta", "max_weight_kg": 400, "radius_km": 30, "available": True, "materials_accepted": ["WOOD"]},
        headers=c2_headers,
    )

    replacements = client.get(f"/api/v1/pickups/{pickup_id}/replacements", headers=donor_headers)
    assert replacements.status_code == 200
    assert len(replacements.json()) >= 1
    assert any(c["collector_id"] == c2_id for c in replacements.json())

    # PASO 12: Nuevo recolector retira — need new match since old one is COMPLETED/cancelled
    # Create a fresh material + match for the second leg
    material2 = client.post(
        "/api/v1/materials",
        json={"name": "10 tablas más", "category": "WOOD", "quantity": 10, "unit": "unit", "condition": "GOOD", "estimated_weight_kg": 60},
        headers=donor_headers,
    ).json()
    need2 = client.post(
        "/api/v1/needs",
        json={"material_category": "WOOD", "quantity_required": 8, "unit": "unit", "priority": "MEDIUM"},
        headers=org_headers,
    ).json()
    matches2 = client.post(f"/api/v1/matches/generate/{material2['id']}", headers=donor_headers).json()
    match2_id = matches2["matches"][0]["id"]
    client.post(f"/api/v1/matches/{match2_id}/accept", headers=donor_headers)
    pickup2 = client.post(
        "/api/v1/pickups",
        json={"match_id": match2_id, "collector_id": c2_id, "pickup_address": "Calle 1", "delivery_address": "Sede 2"},
        headers=donor_headers,
    ).json()

    client.post(f"/api/v1/pickups/{pickup2['id']}/accept", headers=c2_headers)
    client.post(f"/api/v1/pickups/{pickup2['id']}/start", headers=c2_headers)
    client.post(f"/api/v1/pickups/{pickup2['id']}/pickup", headers=c2_headers)

    # PASO 13: Entrega a fundación
    deliver = client.post(f"/api/v1/pickups/{pickup2['id']}/deliver", headers=c2_headers)
    assert deliver.json()["status"] == "DELIVERED"

    # PASO 14: Fundación registra impacto
    impact = client.post(
        "/api/v1/impact",
        json={"match_id": match2_id, "description": "Las tablas fueron utilizadas para construir tres mesas.", "final_use": "Mobiliario comunitario", "weight_reused_kg": 50, "people_benefited": 15},
        headers=org_headers,
    )
    assert impact.status_code == 201

    # PASO 15: Sistema muestra impacto
    stats = client.get("/api/v1/impact/stats", headers=donor_headers)
    assert stats.status_code == 200
    assert stats.json()["total_weight_reused_kg"] >= 50
    assert stats.json()["organizations_helped"] >= 1

    # Verify notifications were generated
    notifs = client.get("/api/v1/notifications", headers=donor_headers)
    assert notifs.status_code == 200
    assert len(notifs.json()) >= 1
