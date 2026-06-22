"""Pytest tests for the TaskFlow repository (Module 05).

Runs against an in-memory SQLite database so NO PostgreSQL is required. Each
test gets its own fresh database and a session that is rolled back and disposed
on teardown, keeping tests fully isolated.

Test:
    pytest code/module-05-tests.py -v
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


repo = _load("module-05-example.py", "module_05_example")


@pytest.fixture
def session():
    # A fresh in-memory database per test => perfect isolation, no Postgres.
    # StaticPool keeps a single connection so the in-memory DB survives.
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
        sess.rollback()  # discard anything uncommitted
        sess.close()
        engine.dispose()  # drop the in-memory database entirely


def test_create_and_get_task(session):
    created = repo.create_task(session, "Ship release", priority="high")
    fetched = repo.get_task(session, created.id)
    assert fetched is not None
    assert fetched.title == "Ship release"
    assert fetched.priority == "high"


def test_get_task_missing_returns_none(session):
    assert repo.get_task(session, 9999) is None


def test_list_tasks_only_open_excludes_done(session):
    repo.create_task(session, "Open one", priority="high")
    done = repo.create_task(session, "Closed one", priority="low")
    repo.update_task(session, done.id, done=True)

    open_titles = [t.title for t in repo.list_tasks(session, only_open=True)]
    assert "Open one" in open_titles
    assert "Closed one" not in open_titles


def test_update_task_changes_fields(session):
    task = repo.create_task(session, "Draft", priority="low")
    updated = repo.update_task(session, task.id, priority="high", done=True)
    assert updated.priority == "high"
    assert updated.done is True


def test_update_task_missing_returns_none(session):
    assert repo.update_task(session, 9999, done=True) is None


def test_delete_task_removes_row(session):
    task = repo.create_task(session, "Temp")
    assert repo.delete_task(session, task.id) is True
    assert repo.get_task(session, task.id) is None


def test_create_project_safe_duplicate_raises_clean_error(session):
    repo.create_project_safe(session, "Launch")
    with pytest.raises(ValueError):
        repo.create_project_safe(session, "Launch")  # UNIQUE name violation
