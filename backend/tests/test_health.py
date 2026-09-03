from __future__ import annotations


def test_health_root(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health_api(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200


def test_health_db(client):
    resp = client.get("/api/v1/health/db")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
