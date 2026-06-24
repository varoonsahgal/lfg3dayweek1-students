# Module 04 — PostgreSQL Fundamentals & SQLAlchemy Models

## Overview

So far TaskFlow forgets everything when the program ends. In this module it gains **memory**. You'll learn relational database fundamentals in **PostgreSQL 14+** (tables, keys, relationships, constraints, indexes, connection strings, users and permissions), then define **SQLAlchemy 2.x** models using the modern `DeclarativeBase` / `Mapped` / `mapped_column` style. By the end you'll connect Python to a real Postgres database, create your schema from your models, and insert your first rows.

This is the bridge between "Python objects in memory" and "data that survives restarts, deploys, and weeks of use."

## Why This Matters

Almost every backend service is, at its core, a careful conversation with a database. Get the data model right — the tables, the keys, the relationships, the constraints — and the rest of the system has a solid foundation. Get it wrong and you fight data corruption, duplicates, and impossible-to-answer queries forever. Modeling well, and connecting securely (credentials in `.env`, never hardcoded), is a core professional skill.

## Why This Matters — Secure-Coding Callout

> **Credentials never touch source code.** Your database username and password live in `.env` and are read at runtime via environment variables. A connection string committed to Git is a leaked password. This habit, started in Module 01, becomes load-bearing here.

## Learning Objectives

By the end of this module, you can:

- Explain relational fundamentals: tables, rows/columns, primary keys, foreign keys, relationships, constraints, and indexes (conceptually).
- Build a PostgreSQL connection string and connect from Python.
- Reason about database users and permissions at a basic level.
- Define SQLAlchemy 2.x models with typed columns, primary keys, and a foreign-key relationship (`Task` and `Project`).
- Create tables from models and insert initial data.

## Prerequisites

- Module 02 (Python, classes), Module 03 (testing habits).
- PostgreSQL 14+ installed locally **or** via the Docker fallback below; `psql` available.

## Key Concepts

### 1. Relational fundamentals

A relational database stores data in **tables** (rows and columns). Two ideas make it powerful:

- **Primary key (PK):** a column that uniquely identifies each row (usually `id`).
- **Foreign key (FK):** a column that references another table's primary key, creating a **relationship**.

TaskFlow has a classic **one-to-many** relationship: one `Project` has many `Task`s.

#### Visual:

<img width="914" height="486" alt="Screenshot 2026-06-23 at 9 31 44 AM" src="https://github.com/user-attachments/assets/096236f9-2f24-47d1-9a50-12c585cedfec" />


**Constraints** protect data integrity:

| Constraint | Meaning | TaskFlow example |
|---|---|---|
| `NOT NULL` | value required | a task must have a `title` |
| `UNIQUE` | no duplicates | a project `name` is unique |
| `CHECK` | value must satisfy a rule | `priority IN ('low','medium','high')` |

An **index** speeds up lookups on a column (conceptually, a sorted shortcut). PKs are indexed automatically; you add indexes to columns you frequently filter by.

> **🧠 Remember:** Constraints are the database's *last line of defense*. Application code can have bugs, validation can be skipped, two requests can race — but a `NOT NULL` or `UNIQUE` constraint is enforced no matter what path the data took. It's the one check nothing can bypass.

### 2. Connection strings and `.env`

A connection string tells Python how to reach Postgres:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME
```

Store it safely:

```text
# .env  (never committed)
DATABASE_URL=postgresql+psycopg://taskflow:secret@localhost:5432/taskflow
```

```python
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]   # fail fast if missing
```
<img width="708" height="535" alt="Screenshot 2026-06-23 at 10 22 10 PM" src="https://github.com/user-attachments/assets/9979f5f4-0ddb-4a94-bb5e-fe8669f35841" />

> **⚖️ Tradeoff:** `os.environ["DATABASE_URL"]` crashes loudly if the variable is missing; `os.environ.get(...)` returns `None` and fails later with a confusing error. At startup, prefer the loud crash — a clear "missing config" failure beats a mysterious one ten layers deep.

### 3. Setting up Postgres

**Option A — Local install** (macOS example):

```bash
psql --version                       # confirm 14+
createdb taskflow                    # create the database
psql taskflow                        # open a SQL shell
```

**Option B — Docker fallback** (recommended if local install is painful):

```bash
docker run --name taskflow-db \
  -e POSTGRES_USER=taskflow \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=taskflow \
  -p 5432:5432 -d postgres:16

# connect with psql to verify
psql "postgresql://taskflow:secret@localhost:5432/taskflow"
```

> **Callout — Users and permissions.** The user in your connection string needs rights to create tables and read/write rows in this database. For the course a single owning user is fine; in production you'd grant least-privilege access per service.

### 4. SQLAlchemy 2.x models

SQLAlchemy is an **ORM** (Object-Relational Mapper): you write Python classes, it manages SQL. Use the modern 2.x style:

```python
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

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

Notice how `Mapped[int]` / `mapped_column(...)` declares both the Python type and the database column, and `relationship(...)` wires the two-way link.

### 5. Creating the schema and inserting data

The **engine** is SQLAlchemy's connection manager:

```python
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL, echo=True)   # echo logs SQL — great for learning
Base.metadata.create_all(engine)                  # creates tables from your models
```

> **🏭 In production:** You create *one* engine for the whole app and reuse it — it manages a pool of reusable connections under the hood. Opening a fresh connection per request would be slow and would exhaust the database's connection limit under load. `echo=True` is a learning aid; turn it off in production or your logs will drown in SQL.

> **Callout — Engine vs. session.** The *engine* manages connections to the database. The *session* (Module 05) manages your unit of work — adding, querying, and committing rows. Today you create the schema; next module you'll work with data through sessions.

## Example Walkthrough

The companion file `code/module-04-example.py` contains the `Project` and `Task` models above, builds an engine from the env-driven `DATABASE_URL`, calls `create_all`, and inserts a sample project with a couple of tasks. Run it:

```bash
python code/module-04-example.py
```

Then verify the data landed using `psql`:

```sql
\dt                      -- list tables: you should see projects and tasks
SELECT * FROM projects;  -- see your seed project
SELECT * FROM tasks;     -- see your seed tasks with their project_id
```

The companion `code/module-04-starter.py` has partial models with `TODO`s: add a field, add a constraint, and wire the relationship.

## Common Mistakes or Misunderstandings

- **Hardcoding the connection string.** Read it from `.env`; never commit credentials.
- **Forgetting `create_all`.** Models without `create_all` mean no tables exist yet.
- **Wrong driver.** Use `postgresql+psycopg://...` and install the matching driver (e.g., `pip install "psycopg[binary]"`).
- **Confusing engine with session.** The engine connects; the session does the work (next module).
- **Skipping constraints.** A model with no `NOT NULL`/`UNIQUE` rules lets bad data in.

## Before You Start the Lab

In the lab you'll stand up a Postgres database, define the TaskFlow schema in SQLAlchemy, create the tables, insert seed rows, and verify with `psql`. Confirm now that you can connect:

```bash
psql "$DATABASE_URL" -c "SELECT 1;"   # should print a 1
```

---

### Short Exercise 1 — Connect and create the schema

- **Estimated Time:** 12 min
- **Goal:** Drive Postgres from Python end to end.
- **Starter Context:** A running Postgres (local or Docker) and `DATABASE_URL` in `.env`.
- **Task Instructions:**
  1. Load `DATABASE_URL` from `.env`.
  2. Build an engine with `create_engine(DATABASE_URL, echo=True)`.
  3. Call `Base.metadata.create_all(engine)` with the example models.
  4. Confirm in `psql` with `\dt`.
- **Success Criteria:** `projects` and `tasks` tables exist in the database.
- **Expected Result:** `\dt` lists both tables; the echoed SQL shows `CREATE TABLE` statements.
- **Optional Hint:** If connection fails, check host/port and that the container/server is running.
- **Key Takeaway:** Your models *are* your schema. Generating tables from Python keeps the database definition in version control and in sync with the code.

---

### Short Exercise 2 — Add a column and a constraint

- **Estimated Time:** 12 min
- **Goal:** Strengthen the schema with a new field and a rule.
- **Starter Context:** `code/module-04-starter.py` with the partial `Task` model.
- **Task Instructions:**
  1. Add a `due_date: Mapped[datetime | None] = mapped_column(nullable=True)`.
  2. Make `Project.name` `unique=True` (if not already).
  3. Drop and recreate the tables, then inspect with `psql \d tasks`.
- **Success Criteria:** `tasks` has a `due_date` column; duplicate project names are rejected.
- **Expected Result:** Inserting two projects with the same name raises an integrity error.
- **Optional Hint:** For a clean reset in the course DB you can `DROP TABLE` then re-run `create_all`.
- **Key Takeaway:** Constraints are guardrails enforced by the database itself — the most reliable place to protect data integrity, because no application bug can bypass them.

---

### Short Exercise 3 — Model and use the relationship

- **Estimated Time:** 15 min
- **Goal:** Wire the one-to-many link and insert related rows.
- **Starter Context:** `Project` and `Task` models with the relationship `TODO`.
- **Task Instructions:**
  1. Ensure `Task.project_id` is a `ForeignKey("projects.id")`.
  2. Add `relationship(back_populates=...)` on both sides.
  3. Create one project, attach two tasks via the relationship, and insert.
  4. Verify each task's `project_id` in `psql`.
- **Success Criteria:** Two tasks reference the same project's `id`.
- **Expected Result:** `SELECT title, project_id FROM tasks;` shows both tasks pointing to your project.
- **Optional Hint:** Appending `Task` objects to `project.tasks` lets SQLAlchemy set the FK for you.
- **Key Takeaway:** Relationships turn separate tables into a connected model. Expressing them in the schema lets the database guarantee that every task belongs to a real project.

---

## Using Claude Code in This Module

**When to use it:**
- **Explain** a model or a connection string line by line.
- **Inspect** your schema and suggest missing constraints.
- **Debug** a connection or driver error.

**Prompts to try:**
1. *"Explain each part of this SQLAlchemy 2.x model and what SQL it will generate, including the foreign key and relationship."*
2. *"My connection string is `postgresql+psycopg://...` and I get a driver error. What's likely wrong and how do I confirm the driver is installed?"*

> **Always validate.** Run `create_all` with `echo=True` and read the generated SQL yourself to confirm Claude Code's explanation matches reality. Never paste a real password into a prompt — use a placeholder.

**If Claude Code is unavailable:** Read the echoed SQL and the SQLAlchemy 2.x docs. The echoed `CREATE TABLE` output is the ground truth for what your models actually produce.

## Key Takeaways

- Relational data = tables, primary keys, foreign keys, relationships, constraints, indexes.
- Connection strings and credentials live in `.env`, never in code or Git.
- SQLAlchemy 2.x models (`DeclarativeBase`, `Mapped`, `mapped_column`, `relationship`) define your schema in Python.
- The engine connects and `create_all` builds tables; sessions (next) do the data work.
- Constraints enforced by the database are your strongest integrity guarantee.

**Next:** In **Module 05 — SQLAlchemy Sessions, Queries, Transactions & Testing DB Code**, you'll build TaskFlow's data-access layer: full CRUD, filtered queries, transactions with rollback, and tests for database code.
