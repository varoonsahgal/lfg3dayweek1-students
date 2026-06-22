"""TaskFlow REST API — STARTER (Module 06).

Complete the TODOs and FIX the bug: create_task_route returns 200 even when
validation fails -- it should return 422 on bad input and only 201 on success.
A reference lives in code/module-06-example.py.

This module imports without a database connection (the engine is built when
create_app is called).
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


repo = _load("module-05-example.py", "module_05_example_starter_api")

ALLOWED_PRIORITIES = {"low", "medium", "high"}


def serialize(task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "done": task.done,
        "project_id": task.project_id,
    }


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
        data = request.get_json(silent=True) or {}
        # 🧩 Debug/Fix: this returns 200 with an error body when the title is
        # missing. It should reject invalid input with 422 and only return 201
        # on success.
        if not data.get("title"):
            return jsonify({"error": "title is required"}), 200  # BUG: wrong status code
        with session_factory() as session:
            task = repo.create_task(
                session,
                title=data["title"].strip(),
                priority=data.get("priority") or "medium",
            )
            return jsonify(serialize(task)), 201

    @app.get("/api/v1/tasks/<int:task_id>")
    def get_task_route(task_id: int):
        # TODO: return 200 + task JSON when found, 404 + error JSON when not.
        raise NotImplementedError("Implement get_task_route in the lab")

    # TODO: add GET /api/v1/tasks (list), PUT, and DELETE routes.
    # TODO: add 404 and 500 error handlers that return generic JSON
    #       (never a stack trace or raw database error).

    return app
