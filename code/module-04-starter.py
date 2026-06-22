"""TaskFlow SQLAlchemy models — STARTER (Module 04).

Complete the TODOs:
  1. Add a `due_date` column to Task (nullable datetime).
  2. Add a UNIQUE constraint on Project.name and a CHECK on Task.priority.
  3. Wire the Project <-> Task one-to-many relationship (back_populates).

This module imports without a database connection. A reference implementation
lives in code/module-04-example.py.

Run (after completing TODOs and starting Postgres):
    python code/module-04-starter.py
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: make `name` UNIQUE so two projects can't share a name.
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    # TODO: add a one-to-many relationship to Task (back_populates="project").


class Task(Base):
    __tablename__ = "tasks"
    # TODO: add __table_args__ with a CHECK constraint limiting priority
    #       to ('low','medium','high').

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    done: Mapped[bool] = mapped_column(default=False)
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"), nullable=True
    )

    # TODO: add a `due_date` column (nullable datetime).
    # TODO: add the matching relationship back to Project (back_populates="tasks").
