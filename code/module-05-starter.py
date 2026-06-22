"""TaskFlow repository — STARTER (Module 05).

Complete the TODOs and FIX the session bug: create_task_buggy never commits,
so the row is silently lost. A reference lives in code/module-05-example.py.

Importing this module does NOT require a database connection.
"""

from __future__ import annotations

import importlib.util
import os
import sys

from sqlalchemy import select  # noqa: F401  (you'll need this for list_open_tasks)
from sqlalchemy.orm import Session


def _load_models():
    path = os.path.join(os.path.dirname(__file__), "module-04-example.py")
    spec = importlib.util.spec_from_file_location("module_04_example_starter", path)
    module = importlib.util.module_from_spec(spec)
    # Register in sys.modules so SQLAlchemy can resolve the models' string type
    # annotations (the models use `from __future__ import annotations`).
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_models = _load_models()
Task = _models.Task


# 🧩 Debug/Fix: this function adds the task but forgets to commit, so nothing is
# ever saved. The code runs with no error, yet get_task returns None later.
def create_task_buggy(session: Session, title: str, priority: str = "medium") -> Task:
    task = Task(title=title, priority=priority)
    session.add(task)
    # BUG: missing session.commit() -- add it to persist the row.
    return task


def get_task(session: Session, task_id: int) -> Task | None:
    """Return a task by id, or None if missing."""
    # TODO: use session.get(Task, task_id).
    raise NotImplementedError("Implement get_task in the lab")


def list_open_tasks(session: Session) -> list[Task]:
    """Return tasks that are not done, highest priority first."""
    # TODO: build a select() with .where(Task.done == False) and .order_by(...).
    raise NotImplementedError("Implement list_open_tasks in the lab")
