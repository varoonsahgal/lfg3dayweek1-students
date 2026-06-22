"""Pytest API tests for the TaskFlow Flask app (Module 06).

Uses Flask's test client against an in-memory SQLite database, so NO PostgreSQL
is required. Each test gets a fresh app (and thus a fresh database).

Test:
    pytest code/module-06-tests.py -v
"""

import importlib.util
import os

import pytest


def _load(filename, module_name):
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


api = _load("module-06-example.py", "module_06_example")


@pytest.fixture
def client():
    app = api.create_app({"TESTING": True, "DATABASE_URL": "sqlite://"})
    return app.test_client()


def test_create_task_returns_201(client):
    resp = client.post("/api/v1/tasks", json={"title": "Write tests"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["title"] == "Write tests"
    assert body["done"] is False


def test_create_task_missing_title_returns_422(client):
    resp = client.post("/api/v1/tasks", json={})
    assert resp.status_code == 422
    assert "fields" in resp.get_json()


def test_create_task_malformed_json_returns_400(client):
    resp = client.post(
        "/api/v1/tasks", data="not json", content_type="application/json"
    )
    assert resp.status_code == 400


def test_invalid_priority_returns_422(client):
    resp = client.post("/api/v1/tasks", json={"title": "Bad", "priority": "urgent"})
    assert resp.status_code == 422


def test_get_missing_task_returns_404(client):
    resp = client.get("/api/v1/tasks/9999")
    assert resp.status_code == 404


def test_list_and_get_roundtrip(client):
    created = client.post(
        "/api/v1/tasks", json={"title": "Roundtrip", "priority": "high"}
    ).get_json()

    listed = client.get("/api/v1/tasks")
    assert listed.status_code == 200
    assert any(t["id"] == created["id"] for t in listed.get_json())

    one = client.get(f"/api/v1/tasks/{created['id']}")
    assert one.status_code == 200
    assert one.get_json()["priority"] == "high"


def test_update_and_delete(client):
    created = client.post("/api/v1/tasks", json={"title": "Edit me"}).get_json()

    updated = client.put(
        f"/api/v1/tasks/{created['id']}", json={"done": True, "priority": "high"}
    )
    assert updated.status_code == 200
    assert updated.get_json()["done"] is True

    deleted = client.delete(f"/api/v1/tasks/{created['id']}")
    assert deleted.status_code == 200
    assert client.get(f"/api/v1/tasks/{created['id']}").status_code == 404
