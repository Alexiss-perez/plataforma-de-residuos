from __future__ import annotations


def test_post_location_hidden_for_non_author(client, auth_headers):
    post = client.post(
        "/api/v1/posts",
        json={"type": "OFFER", "title": "Tengo madera", "description": "20 tablas", "latitude": -33.45, "longitude": -70.66, "commune": "Providencia"},
        headers=auth_headers,
    )
    assert post.status_code == 201
    post_id = post.json()["id"]

    other = client.post("/api/v1/auth/register", json={"name": "Other", "email": "other_priv@example.com", "password": "pass12345"})
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}

    resp = client.get(f"/api/v1/posts/{post_id}", headers=other_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["latitude"] is None
    assert data["longitude"] is None
    assert data["commune"] == "Providencia"


def test_post_location_visible_for_author(client, auth_headers):
    post = client.post(
        "/api/v1/posts",
        json={"type": "OFFER", "title": "Tengo madera", "latitude": -33.45, "longitude": -70.66, "commune": "Providencia"},
        headers=auth_headers,
    )
    post_id = post.json()["id"]
    resp = client.get(f"/api/v1/posts/{post_id}", headers=auth_headers)
    assert resp.json()["latitude"] == -33.45
