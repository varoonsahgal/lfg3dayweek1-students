"""TaskFlow SQLAlchemy models (Module 04 reference example).

Defines the one-to-many schema -- one Project has many Tasks -- using the
modern SQLAlchemy 2.x declarative style (DeclarativeBase, Mapped,
mapped_column, relationship).

Importing this module does NOT touch a database. Only the __main__ demo below
connects, creates tables, and inserts a sample project against DATABASE_URL.

Run (needs PostgreSQL):
    python code/module-04-example.py
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, ForeignKey, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all TaskFlow models."""


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    # UNIQUE: two projects cannot share a name (enforced by the database).
    name: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    # One project has many tasks.
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, name={self.name!r})"


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        # The database itself guarantees priority is always one of these values.
        CheckConstraint(
            "priority in ('low','medium','high')", name="ck_task_priority"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    priority: Mapped[str] = mapped_column(String(10), default="medium")
    done: Mapped[bool] = mapped_column(default=False)
    # Nullable so a task can exist before it is filed under a project.
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"), nullable=True
    )

    project: Mapped["Project | None"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, title={self.title!r}, "
            f"priority={self.priority!r}, done={self.done})"
        )


# Default points at a local Postgres. The driver form is postgresql+psycopg
# (install with: pip install "psycopg[binary]"). Real credentials belong in .env.
DEFAULT_DATABASE_URL = "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow"


def get_engine(database_url: str | None = None, echo: bool = False):
    """Build an engine from the given URL or the DATABASE_URL env var."""
    url = database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    return create_engine(url, echo=echo)


def create_all(engine) -> None:
    """Create all TaskFlow tables on the given engine."""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    from sqlalchemy.orm import Session

    # echo=True prints the generated SQL so you can read what your models produce.
    engine = get_engine(echo=True)
    create_all(engine)

    with Session(engine) as session:
        project = Project(name="Launch")
        project.tasks.append(Task(title="Ship release", priority="high"))
        project.tasks.append(Task(title="Write docs", priority="low"))
        session.add(project)
        session.commit()  # without commit, nothing is saved
        print(f"Inserted project {project.id} with {len(project.tasks)} tasks")
