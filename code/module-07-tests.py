"""Pytest suite for the integrated TaskFlow service + capstone feature (Module 07).

Covers the new data-access logic (unit tests) and the API (Flask test client)
over an in-memory SQLite database. NO PostgreSQL required.

Test:
    pytest code/module-07-tests.py -v
"""

import importlib.util
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


def _load(filename, module_name):
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


service = _load("module-07-example.py", "module_07_example")
repo = service.repo


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    repo.create_all(engine)
    sess = Session(engine)
    try:
        yield sess
    finally:
        sess.rollback()
        sess.close()
        engine.dispose()


@pytest.fixture
def client():
    app = service.create_app({"TESTING": True, "DATABASE_URL": "sqlite://"})
    return app.test_client()


# --- unit tests for the capstone data-access functions ------------------------

def test_complete_task_sets_done(session):
    task = repo.create_task(session, "Finish me", priority="high")
    completed = service.complete_task(session, task.id)
    assert completed.done is True


def test_complete_task_missing_returns_none(session):
    assert service.complete_task(session, 9999) is None


def test_list_tasks_by_status_open_excludes_done(session):
    repo.create_task(session, "Open task", priority="high")
    done = repo.create_task(session, "Done task", priority="low")
    service.complete_task(session, done.id)

    open_titles = [t.title for t in service.list_tasks_by_status(session, "open")]
    assert "Open task" in open_titles
    assert "Done task" not in open_titles


# --- API tests (full vertical slice) -----------------------------------------

def test_create_and_complete_via_api(client):
    created = client.post("/api/v1/tasks", json={"title": "Ship"}).get_json()
    resp = client.post(f"/api/v1/tasks/{created['id']}/complete")
    assert resp.status_code == 200
    assert resp.get_json()["done"] is True


def test_complete_missing_task_returns_404(client):
    resp = client.post("/api/v1/tasks/9999/complete")
    assert resp.status_code == 404


def test_status_filter_returns_only_open(client):
    a = client.post("/api/v1/tasks", json={"title": "A"}).get_json()
    client.post("/api/v1/tasks", json={"title": "B"})
    client.post(f"/api/v1/tasks/{a['id']}/complete")  # complete A

    resp = client.get("/api/v1/tasks?status=open")
    assert resp.status_code == 200
    titles = [t["title"] for t in resp.get_json()]
    assert "B" in titles
    assert "A" not in titles


def test_invalid_status_returns_422(client):
    resp = client.get("/api/v1/tasks?status=bogus")
    assert resp.status_code == 422
