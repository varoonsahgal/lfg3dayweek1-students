"""TaskFlow data-access layer / repository (Module 05 reference example).

CRUD over the Module 04 models using SQLAlchemy sessions, plus a filtered
query, a transactional multi-step operation, and safe error handling.

Every function takes a `session`, so it can run against any engine -- PostgreSQL
in production, in-memory SQLite in tests. Importing this module does NOT require
a database connection.

Run (needs PostgreSQL):
    python code/module-05-example.py
Test (no PostgreSQL needed):
    pytest code/module-05-tests.py -v
"""

from __future__ import annotations

import importlib.util
import os
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker


def _load_models():
    # The models file has hyphens in its name, so load it by path.
    path = os.path.join(os.path.dirname(__file__), "module-04-example.py")
    spec = importlib.util.spec_from_file_location("module_04_example", path)
    module = importlib.util.module_from_spec(spec)
    # Register in sys.modules so SQLAlchemy can resolve the models' string type
    # annotations (the models use `from __future__ import annotations`).
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_models = _load_models()
Base = _models.Base
Project = _models.Project
Task = _models.Task


# --- engine / session helpers -------------------------------------------------

def create_all(engine) -> None:
    """Create all TaskFlow tables on the given engine."""
    Base.metadata.create_all(engine)


def make_session_factory(engine) -> sessionmaker:
    """Return a sessionmaker bound to the given engine."""
    return sessionmaker(bind=engine)


# --- create -------------------------------------------------------------------

def create_project(session: Session, name: str) -> Project:
    """Create and persist a project."""
    project = Project(name=name)
    session.add(project)
    session.commit()
    return project


def create_task(
    session: Session,
    title: str,
    project_id: int | None = None,
    priority: str = "medium",
) -> Task:
    """Create and persist a task. Persistence only happens on commit()."""
    task = Task(title=title, project_id=project_id, priority=priority)
    session.add(task)
    session.commit()  # without this, nothing is saved
    return task


# --- read ---------------------------------------------------------------------

def get_task(session: Session, task_id: int) -> Task | None:
    """Return a task by id, or None if it does not exist."""
    return session.get(Task, task_id)


def list_tasks(session: Session, *, only_open: bool = False) -> list[Task]:
    """List tasks, optionally only those not done, ordered by priority.

    Uses select() so the query is parameterized and safe from SQL injection --
    we never build a SQL string from input.
    """
    stmt = select(Task)
    if only_open:
        stmt = stmt.where(Task.done == False)  # noqa: E712 (SQL boolean, not Python)
    stmt = stmt.order_by(Task.priority.desc())
    return list(session.scalars(stmt).all())


# --- update / delete ----------------------------------------------------------

def update_task(session: Session, task_id: int, **changes) -> Task | None:
    """Update fields on a task; return the task, or None if not found."""
    task = session.get(Task, task_id)
    if task is None:
        return None
    for field, value in changes.items():
        setattr(task, field, value)
    session.commit()
    return task


def delete_task(session: Session, task_id: int) -> bool:
    """Delete a task; return True if a row was removed."""
    task = session.get(Task, task_id)
    if task is None:
        return False
    session.delete(task)
    session.commit()
    return True


# --- transaction (atomic, all-or-nothing) ------------------------------------

def move_task_to_project(
    session: Session, task_id: int, new_project_id: int
) -> Task:
    """Move a task to another project as one atomic unit of work."""
    try:
        task = session.get(Task, task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        task.project_id = new_project_id
        # ... imagine an additional related change here ...
        session.commit()  # both changes persist together
        return task
    except SQLAlchemyError:
        session.rollback()  # undo everything on failure
        raise


# --- safe error handling ------------------------------------------------------

def create_project_safe(session: Session, name: str) -> Project:
    """Create a project, translating DB errors into a safe, generic message."""
    try:
        project = Project(name=name)
        session.add(project)
        session.commit()
        return project
    except SQLAlchemyError:
        session.rollback()
        # Don't leak raw DB details (table names, constraints) to the caller.
        raise ValueError(f"A project named {name!r} already exists")


if __name__ == "__main__":
    # Exercises CRUD against the real database in DATABASE_URL.
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow",
    )
    engine = create_engine(url)
    create_all(engine)
    SessionLocal = make_session_factory(engine)
    with SessionLocal() as session:
        project = create_project(session, name="Launch")
        create_task(session, "Ship release", project_id=project.id, priority="high")
        create_task(session, "Write docs", project_id=project.id, priority="low")
        print("open tasks:", [t.title for t in list_tasks(session, only_open=True)])
