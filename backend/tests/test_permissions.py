from __future__ import annotations


def test_natural_cannot_update_other_org(client, auth_headers):
    resp = client.post(
        "/api/v1/organizations",
        json={"name": "My Org", "type": "NGO", "commune": "Santiago"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    my_org_id = resp.json()["id"]

    other = client.post(
        "/api/v1/auth/register",
        json={"name": "Other", "email": "other@example.com", "password": "pass12345", "role": "ORGANIZATION"},
    )
    other_token = other.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    resp2 = client.patch(
        f"/api/v1/organizations/{my_org_id}",
        json={"name": "Hacked"},
        headers=other_headers,
    )
    assert resp2.status_code == 403


def test_user_cannot_edit_other_material(client, auth_headers):
    resp = client.post(
        "/api/v1/materials",
        json={"name": "My wood", "category": "WOOD", "quantity": 5, "unit": "unit", "condition": "GOOD"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    mat_id = resp.json()["id"]

    other = client.post(
        "/api/v1/auth/register",
        json={"name": "Other", "email": "other2@example.com", "password": "pass12345"},
    )
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    resp2 = client.patch(
        f"/api/v1/materials/{mat_id}",
        json={"name": "Stolen"},
        headers=other_headers,
    )
    assert resp2.status_code == 403
