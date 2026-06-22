# Module 04 Lab — Give TaskFlow Memory with PostgreSQL & SQLAlchemy

## Overview

TaskFlow forgets everything when the program ends. In this lab it gains memory. You'll stand up a PostgreSQL database (local or Docker), define the TaskFlow schema with SQLAlchemy 2.x models (`Project` and `Task`, one-to-many), create the tables from your models, seed rows, and verify the data with `psql`. Credentials stay in `.env` — never in code.

## Learning Objectives

By the end of this lab you will be able to:

- Run a PostgreSQL database locally or via Docker and connect with `psql`.
- Build a connection string and load it from `.env`.
- Define SQLAlchemy 2.x models with `DeclarativeBase`, `Mapped`, and `mapped_column`.
- Model a one-to-many relationship with a foreign key and `relationship()`.
- Create tables with `Base.metadata.create_all` and insert seed data.
- Add a column and a constraint, and verify with `psql`.

## Prerequisites

- Modules 02–03 complete (Python, classes, testing habits).
- PostgreSQL 14+ installed **or** Docker available.
- `psql` on your PATH.

## Estimated Time

~60–75 minutes (core path). Short challenge exercises add ~40 minutes.

## Environment and Setup

Install the driver and SQLAlchemy:
```bash
cd taskflow
source .venv/bin/activate
pip install "sqlalchemy>=2.0" "psycopg[binary]" python-dotenv
pip freeze > requirements.txt
git checkout -b feature/db-models
```

Start Postgres — **Option A (local)**:
```bash
psql --version          # confirm 14+
createdb taskflow
```

**Option B (Docker fallback, recommended if local install is painful):**
```bash
docker run --name taskflow-db \
  -e POSTGRES_USER=taskflow \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=taskflow \
  -p 5432:5432 -d postgres:16
```

Put the connection string in `.env` (never commit it):
```text
DATABASE_URL=postgresql+psycopg://taskflow:secret@localhost:5432/taskflow
```

Verify the connection:
```bash
psql "$DATABASE_URL" -c "SELECT 1;"     # should print a 1
```

Companion code files (generated separately):

- `code/module-04-example.py` — reference `Project`/`Task` models + `create_all` + seed insert.
- `code/module-04-starter.py` — partial models with `TODO`s.

## Scenario

TaskFlow's product team wants tasks to live in projects and survive restarts. You're the engineer who designs the schema: the tables, keys, relationship, and constraints that will protect TaskFlow's data for the life of the service.

## Tasks

### Task 1: Connect Python to Postgres and create the schema

#### Goal
Generate the TaskFlow tables from SQLAlchemy models.

#### 🔍 Think First (do not skip)
Before writing models, sketch the schema on paper:

- What columns does `projects` need? Which is the primary key? Which should be `UNIQUE`?
- What columns does `tasks` need? How does a task point at its project?
- A task must always belong to a project — which constraint enforces that?

> **💡 Why this matters:** Designing the schema on paper first is cheaper than discovering a missing key after you've written data. Keys and constraints are hard to add *after* bad rows exist — get them right before the first insert.

#### Steps
1. In `app/models.py`, define the base and models:
   ```python
   from datetime import datetime
   from sqlalchemy import ForeignKey, String
   from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


   class Base(DeclarativeBase):
       pass


   class Project(Base):
       __tablename__ = "projects"
       id: Mapped[int] = mapped_column(primary_key=True)
       name: Mapped[str] = mapped_column(String(100), unique=True)
       created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
       tasks: Mapped[list["Task"]] = relationship(back_populates="project")


   class Task(Base):
       __tablename__ = "tasks"
       id: Mapped[int] = mapped_column(primary_key=True)
       title: Mapped[str] = mapped_column(String(200))
       priority: Mapped[str] = mapped_column(String(10), default="medium")
       done: Mapped[bool] = mapped_column(default=False)
       project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
       project: Mapped["Project"] = relationship(back_populates="tasks")
   ```
2. In `app/db.py`, build the engine from `.env` and create the schema:
   ```python
   import os
   from dotenv import load_dotenv
   from sqlalchemy import create_engine
   from app.models import Base

   load_dotenv()
   DATABASE_URL = os.environ["DATABASE_URL"]
   engine = create_engine(DATABASE_URL, echo=True)

   if __name__ == "__main__":
       Base.metadata.create_all(engine)
   ```
3. Run it:
   ```bash
   python -m app.db
   ```

#### Checkpoint
The echoed SQL shows `CREATE TABLE projects` and `CREATE TABLE tasks`.

#### Expected Output (psql)
```sql
taskflow=# \dt
          List of relations
 Schema |   Name    | Type  |  Owner
--------+-----------+-------+----------
 public | projects  | table | taskflow
 public | tasks     | table | taskflow
```

---

### Task 2: Seed related rows

#### Goal
Insert one project with two tasks through the relationship.

#### Steps
1. In a script or `__main__` block, insert seed data:
   ```python
   from sqlalchemy.orm import Session
   from app.db import engine
   from app.models import Project, Task

   with Session(engine) as session:
       project = Project(name="Launch")
       project.tasks = [
           Task(title="Write release notes", priority="high"),
           Task(title="Tag the build", priority="medium"),
       ]
       session.add(project)
       session.commit()
   ```
2. Verify in `psql`.

#### Checkpoint
Both tasks reference the same `project_id`.

#### Expected Output (psql)
```sql
taskflow=# SELECT title, project_id FROM tasks;
       title         | project_id
---------------------+------------
 Write release notes |          1
 Tag the build       |          1
```

> **🏭 In production:** Notice you never typed a `project_id` for the tasks — appending them to `project.tasks` let SQLAlchemy set the foreign key after the project got its `id`. Letting the ORM wire relationships is more reliable than hand-assigning ids you don't yet know.

---

## 🧠 Your Turn — Model the relationship from scratch

Open `code/module-04-starter.py`. The `Task` model is missing its link to `Project`.

- **Goal:** Add `project_id` as a `ForeignKey("projects.id")` and wire `relationship(back_populates=...)` on both `Task` and `Project`.
- **Constraints:** Every task must belong to a project; appending a `Task` to `project.tasks` should set the FK automatically.
- **Expected outcome:** After inserting a project with two appended tasks, both tasks share the project's `id`.

**Hint:** The `back_populates` name on each side must match the attribute name on the other side.

Design it yourself — no full solution here.

---

## 🧩 Debug / Fix — The driver error

A teammate set `DATABASE_URL=postgresql://taskflow:secret@localhost:5432/taskflow` and gets:
```text
ModuleNotFoundError: No module named 'psycopg2'
```

- **Symptom:** SQLAlchemy can't find a driver when creating the engine.
- **Likely cause:** The URL uses the default driver name; the modern driver `psycopg` (v3) is installed, not `psycopg2`.
- **Your task:** Fix the connection string to explicitly select the installed driver and confirm the connection.

**Success criteria:** `python -m app.db` connects and creates tables without a driver error.

**Hint:** The driver goes right after `postgresql+` in the URL.

> **🧠 Remember:** `postgresql://` quietly defaults to the legacy `psycopg2` driver. The dialect and the installed package must match — the `+psycopg` in the URL is what tells SQLAlchemy which driver you actually have.

---

## Short Challenge Exercises

### Exercise A — Add a `due_date` column

- **Estimated Time:** 12 min
- **Goal:** Extend the schema with an optional date.
- **Starter Context:** The `Task` model.
- **Task Instructions:**
  1. Add `due_date: Mapped[datetime | None] = mapped_column(nullable=True)`.
  2. Drop the `tasks` table (`DROP TABLE tasks;` in psql) and re-run `create_all`.
  3. Inspect with `psql \d tasks`.
- **Success Criteria:** `tasks` has a nullable `due_date` column.
- **Expected Result:** `\d tasks` lists `due_date | timestamp | nullable`.
- **Optional Hint:** Nullable means a task can exist without a due date.
- **Key Takeaway:** Your models *are* your schema — change the Python, regenerate, and the database follows.

### Exercise B — Enforce a UNIQUE constraint

- **Estimated Time:** 12 min
- **Goal:** Prevent duplicate project names at the database level.
- **Starter Context:** The `Project` model.
- **Task Instructions:**
  1. Confirm `name` has `unique=True`.
  2. Recreate the table, then try inserting two projects named `"Launch"`.
  3. Observe the integrity error on the second insert.
- **Success Criteria:** The duplicate insert is rejected by the database.
- **Expected Result:** An `IntegrityError` mentioning a unique constraint violation.
- **Optional Hint:** The database enforces this even if your Python code forgets to check.
- **Key Takeaway:** Constraints are guardrails the database enforces — the most reliable place to protect integrity, because no application bug can bypass them.

### Exercise C — Add a CHECK-style validation note

- **Estimated Time:** 12 min
- **Goal:** Reason about where a "priority must be low/medium/high" rule belongs.
- **Starter Context:** The `priority` column on `Task`.
- **Task Instructions:**
  1. In `psql`, manually add a CHECK constraint:
     `ALTER TABLE tasks ADD CONSTRAINT priority_valid CHECK (priority IN ('low','medium','high'));`
  2. Try inserting a task with `priority = 'urgent'` via raw SQL.
  3. Note that the database rejects it.
- **Success Criteria:** The invalid priority insert fails at the DB level.
- **Expected Result:** A check-constraint violation error.
- **Optional Hint:** This is the same allowed-set you validated in Python in Module 02 — now enforced by the DB too.
- **Key Takeaway:** Defense in depth: validate in Python for friendly errors *and* in the database for guaranteed integrity.

---

## Validation / Success Criteria

You are done when:

- [ ] `psql "$DATABASE_URL" -c "SELECT 1;"` returns `1`.
- [ ] `\dt` shows `projects` and `tasks`.
- [ ] Seed data shows two tasks sharing one `project_id`.
- [ ] The relationship is wired on both sides (🧠 Your Turn).
- [ ] The driver error is resolved (🧩 Debug/Fix).
- [ ] `.env` holds the credentials and is **not** committed.

**Definition of Done:** Commit `app/models.py` and `app/db.py` on `feature/db-models` and open a merge request. Confirm in the description that no credentials appear in the diff.

## Troubleshooting

- **Symptom:** `connection refused` on port 5432.
  **Likely cause:** Postgres/container not running.
  **Fix:** Start the service or `docker start taskflow-db`.

- **Symptom:** `KeyError: 'DATABASE_URL'`.
  **Likely cause:** `.env` not loaded or key missing.
  **Fix:** Call `load_dotenv()` and confirm `.env` has `DATABASE_URL`.

- **Symptom:** `No module named 'psycopg2'`.
  **Likely cause:** URL uses the default driver but `psycopg` v3 is installed.
  **Fix:** Use `postgresql+psycopg://...`.

- **Symptom:** `relation "projects" does not exist`.
  **Likely cause:** `create_all` never ran.
  **Fix:** Run `python -m app.db` before inserting.

- **Symptom:** Changing a model didn't change the table.
  **Likely cause:** `create_all` does not alter existing tables.
  **Fix:** For the course DB, `DROP TABLE` then recreate (migrations come later in a real project).

## Stretch Goal / Extension

Add an index to `tasks.project_id` (`index=True` on the column) and re-run `create_all`. In `psql`, run `\d tasks` and confirm the index exists. Reason about why filtering tasks by project will be faster.

## Using Claude Code in This Lab

Ask Claude Code to explain the generated SQL:
> *"Explain each part of this SQLAlchemy 2.x model and what SQL it will generate, including the foreign key and relationship."*

**Required manual verification:** Run `create_all` with `echo=True` and compare the *actual* echoed `CREATE TABLE` SQL against Claude Code's explanation. The echoed SQL is the ground truth. Never paste a real password into a prompt — use a placeholder.

**No-AI fallback:** Read the echoed SQL and the SQLAlchemy 2.x docs directly.

## Key Takeaways

- Relational data = tables, primary keys, foreign keys, relationships, constraints, indexes.
- Connection strings and credentials live in `.env`, never in code.
- SQLAlchemy 2.x models (`DeclarativeBase`/`Mapped`/`mapped_column`/`relationship`) define the schema in Python.
- The engine connects and `create_all` builds tables; sessions do the data work (next module).
- Database-enforced constraints are your strongest integrity guarantee.
