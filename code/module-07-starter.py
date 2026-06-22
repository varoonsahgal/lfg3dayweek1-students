"""TaskFlow integrated service — STARTER (Module 07 capstone).

The base service (create + get a task) is wired for you. Implement the capstone
feature end-to-end:
  * GET  /api/v1/tasks?status=open|done|all   (422 on an invalid status value)
  * POST /api/v1/tasks/<id>/complete          (200 on success, 404 when missing)

A reference lives in code/module-07-example.py. This module imports without a
database (the engine is built in create_app).
"""

from __future__ import annotations

import importlib.util
import os

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, select  # noqa: F401  (needed for the status filter)
from sqlalchemy.pool import StaticPool


def _load(filename, module_name):
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


repo = _load("module-05-example.py", "module_05_example_capstone_starter")
Task = repo.Task

ALLOWED_STATUS = {"open", "done", "all"}


def serialize(task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "done": task.done,
        "project_id": task.project_id,
    }


def complete_task(session, task_id):
    """Mark a task done; return the task, or None if not found."""
    # TODO (capstone): load the task with session.get(Task, task_id); if found,
    #                  set done=True, commit, and return it; otherwise return None.
    raise NotImplementedError("Implement complete_task for the capstone")


def create_app(config: dict | None = None) -> Flask:
    config = config or {}
    app = Flask(__name__)
    app.config.update(config)

    database_url = config.get("DATABASE_URL", "sqlite://")
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    repo.create_all(engine)
    session_factory = repo.make_session_factory(engine)

    @app.post("/api/v1/tasks")
    def create_task_route():
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        if not isinstance(data.get("title"), str) or not data["title"].strip():
            return (
                jsonify({"error": "Validation failed", "fields": {"title": "is required"}}),
                422,
            )
        with session_factory() as session:
            task = repo.create_task(
                session,
                title=data["title"].strip(),
                priority=data.get("priority") or "medium",
            )
            return jsonify(serialize(task)), 201

    @app.get("/api/v1/tasks/<int:task_id>")
    def get_task_route(task_id: int):
        with session_factory() as session:
            task = repo.get_task(session, task_id)
            if task is None:
                return jsonify({"error": "Task not found"}), 404
            return jsonify(serialize(task)), 200

    # TODO (capstone): add GET /api/v1/tasks supporting ?status=open|done|all
    #                  (return 422 for an invalid status value, 200 otherwise).
    # TODO (capstone): add POST /api/v1/tasks/<id>/complete using complete_task
    #                  (return 200 on success, 404 when the task is missing).

    return app
