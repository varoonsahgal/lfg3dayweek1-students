"""TaskFlow REST API (Module 06 reference example).

A Flask 3.x application factory exposing CRUD endpoints for tasks under
/api/v1/tasks, backed by the Module 05 repository. Input is validated
server-side, responses are JSON with correct status codes, and error handlers
never leak stack traces or database details.

Configurable database: defaults to a local SQLite file; tests pass an in-memory
SQLite URL. No PostgreSQL is required to run or test.

Run:
    python code/module-06-example.py        # serves http://127.0.0.1:5000
Test:
    pytest code/module-06-tests.py -v
"""

from __future__ import annotations

import importlib.util
import os

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


def _load(filename, module_name):
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


repo = _load("module-05-example.py", "module_05_example")

ALLOWED_PRIORITIES = {"low", "medium", "high"}


def serialize(task) -> dict:
    """Convert a Task model into a JSON-safe dict."""
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "done": task.done,
        "project_id": task.project_id,
    }


def validate_task_payload(data, *, partial: bool = False) -> dict:
    """Return a dict of field errors (empty dict means valid)."""
    errors: dict[str, str] = {}
    if not isinstance(data, dict):
        return {"body": "must be a JSON object"}
    if not partial or "title" in data:
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            errors["title"] = "is required and must be a non-empty string"
    priority = data.get("priority")
    if priority is not None and priority not in ALLOWED_PRIORITIES:
        errors["priority"] = "must be one of low, medium, high"
    return errors


def _make_engine(database_url: str):
    """Build an engine, using a shared connection for in-memory SQLite."""
    if database_url == "sqlite://" or ":memory:" in database_url:
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    if database_url.startswith("sqlite"):
        return create_engine(database_url, connect_args={"check_same_thread": False})
    return create_engine(database_url)


def create_app(config: dict | None = None) -> Flask:
    """Application factory: build and configure the TaskFlow API."""
    config = config or {}
    app = Flask(__name__)
    app.config.update(config)

    database_url = config.get("DATABASE_URL") or os.environ.get(
        "DATABASE_URL", "sqlite:///taskflow.db"
    )
    engine = _make_engine(database_url)
    repo.create_all(engine)
    session_factory = repo.make_session_factory(engine)

    # --- routes (thin: parse, validate, delegate, respond) --------------------

    @app.get("/api/v1/tasks")
    def list_tasks_route():
        with session_factory() as session:
            tasks = repo.list_tasks(session)
            return jsonify([serialize(t) for t in tasks]), 200

    @app.get("/api/v1/tasks/<int:task_id>")
    def get_task_route(task_id: int):
        with session_factory() as session:
            task = repo.get_task(session, task_id)
            if task is None:
                return jsonify({"error": "Task not found"}), 404
            return jsonify(serialize(task)), 200

    @app.post("/api/v1/tasks")
    def create_task_route():
        data = request.get_json(silent=True)
        if data is None:  # malformed / non-JSON body
            return jsonify({"error": "Request body must be valid JSON"}), 400
        errors = validate_task_payload(data)
        if errors:
            return jsonify({"error": "Validation failed", "fields": errors}), 422
        with session_factory() as session:
            task = repo.create_task(
                session,
                title=data["title"].strip(),
                priority=data.get("priority") or "medium",
                project_id=data.get("project_id"),
            )
            return jsonify(serialize(task)), 201

    @app.put("/api/v1/tasks/<int:task_id>")
    def update_task_route(task_id: int):
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Request body must be valid JSON"}), 400
        errors = validate_task_payload(data, partial=True)
        if errors:
            return jsonify({"error": "Validation failed", "fields": errors}), 422
        changes = {k: v for k, v in data.items() if k in {"title", "priority", "done"}}
        with session_factory() as session:
            task = repo.update_task(session, task_id, **changes)
            if task is None:
                return jsonify({"error": "Task not found"}), 404
            return jsonify(serialize(task)), 200

    @app.delete("/api/v1/tasks/<int:task_id>")
    def delete_task_route(task_id: int):
        with session_factory() as session:
            removed = repo.delete_task(session, task_id)
            if not removed:
                return jsonify({"error": "Task not found"}), 404
            return jsonify({"deleted": True, "id": task_id}), 200

    # --- error handlers (return safe, generic JSON -- never leak internals) ---

    @app.errorhandler(404)
    def handle_404(_err):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_500(_err):
        app.logger.exception("Unhandled error")  # log the real error server-side
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
