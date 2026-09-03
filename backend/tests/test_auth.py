from __future__ import annotations


def test_register(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "pass12345"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alice@example.com"
    assert "password_hash" not in resp.text


def test_register_duplicate(client):
    payload = {"name": "Bob", "email": "bob@example.com", "password": "pass12345"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_success(client):
    client.post("/api/v1/auth/register", json={"name": "Carol", "email": "carol@example.com", "password": "pass12345"})
    resp = client.post("/api/v1/auth/login", json={"email": "carol@example.com", "password": "pass12345"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={"name": "Dave", "email": "dave@example.com", "password": "pass12345"})
    resp = client.post("/api/v1/auth/login", json={"email": "dave@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_me_protected(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client, auth_headers):
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_password_not_exposed(client, auth_headers):
    resp = client.get("/api/v1/auth/me", headers=auth_headers)
    assert "password_hash" not in resp.text
