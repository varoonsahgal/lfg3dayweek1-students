"""TaskFlow integrated service (Module 07 capstone reference).

Wires utilities + repository + Flask API into one runnable service, and adds
two new end-to-end features:
  * GET  /api/v1/tasks?status=open|done|all   (filter tasks by status)
  * POST /api/v1/tasks/<id>/complete          (mark a task done)

SQLite-friendly: runs and tests with no PostgreSQL.

Run:
    python code/module-07-example.py
Test:
    pytest code/module-07-tests.py -v
"""

from __future__ import annotations

import importlib.util
import os

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool


def _load(filename, module_name):
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


repo = _load("module-05-example.py", "module_05_example_capstone")
Task = repo.Task

ALLOWED_PRIORITIES = {"low", "medium", "high"}
ALLOWED_STATUS = {"open", "done", "all"}


def serialize(task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "done": task.done,
        "project_id": task.project_id,
    }


# --- new data-access functions (the capstone feature) -------------------------

def list_tasks_by_status(session, status: str = "all") -> list:
    """List tasks filtered by status: 'open', 'done', or 'all'."""
    stmt = select(Task)
    if status == "open":
        stmt = stmt.where(Task.done == False)  # noqa: E712
    elif status == "done":
        stmt = stmt.where(Task.done == True)   # noqa: E712
    stmt = stmt.order_by(Task.priority.desc())
    return list(session.scalars(stmt).all())


def complete_task(session, task_id: int):
    """Mark a task as done; return the task, or None if it does not exist."""
    task = session.get(Task, task_id)
    if task is None:
        return None
    task.done = True
    session.commit()
    return task


def validate_task_payload(data) -> dict:
    """Return a dict of field errors (empty dict means valid)."""
    errors: dict[str, str] = {}
    if not isinstance(data, dict):
        return {"body": "must be a JSON object"}
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        errors["title"] = "is required and must be a non-empty string"
    priority = data.get("priority")
    if priority is not None and priority not in ALLOWED_PRIORITIES:
        errors["priority"] = "must be one of low, medium, high"
    return errors


def _make_engine(database_url: str):
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
    """Application factory wiring the full TaskFlow service."""
    config = config or {}
    app = Flask(__name__)
    app.config.update(config)

    database_url = config.get("DATABASE_URL") or os.environ.get(
        "DATABASE_URL", "sqlite:///taskflow.db"
    )
    engine = _make_engine(database_url)
    repo.create_all(engine)
    session_factory = repo.make_session_factory(engine)

    @app.get("/api/v1/tasks")
    def list_tasks_route():
        # New feature: optional ?status=open|done|all (defaults to all).
        status = request.args.get("status", "all")
        if status not in ALLOWED_STATUS:
            return (
                jsonify(
                    {
                        "error": "Validation failed",
                        "fields": {"status": "must be open, done, or all"},
                    }
                ),
                422,
            )
        with session_factory() as session:
            tasks = list_tasks_by_status(session, status)
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
        if data is None:
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

    @app.post("/api/v1/tasks/<int:task_id>/complete")
    def complete_task_route(task_id: int):
        # New feature: mark a task done.
        with session_factory() as session:
            task = complete_task(session, task_id)
            if task is None:
                return jsonify({"error": "Task not found"}), 404
            return jsonify(serialize(task)), 200

    @app.errorhandler(404)
    def handle_404(_err):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def handle_500(_err):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
