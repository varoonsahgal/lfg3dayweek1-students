# Module 05 — SQLAlchemy Sessions, Queries, Transactions & Testing DB Code

## Overview

You have a schema (Module 04); now you build the layer that *uses* it. This module is about TaskFlow's **data-access layer** (often called a "repository"): full CRUD with SQLAlchemy sessions, queries with filtering and ordering, loading related rows, and transactions with commit and rollback. You'll learn the **session lifecycle** — the single most common source of database bugs — handle database errors safely, avoid unsafe query patterns, and write tests for database code using a rollback-per-test fixture.

By the end, TaskFlow can reliably create, read, update, and delete data, and recover cleanly when something goes wrong.

## Why This Matters

The data-access layer is where most real backend bugs live: a forgotten `commit`, a session left open, a half-finished multi-step operation that corrupts data, or a query that concatenates user input and opens an SQL-injection hole. Getting this layer right — predictable sessions, atomic transactions, safe errors, parameterized queries — is what separates a toy script from a service you'd trust with real data.

> **Secure-coding callouts (this module):** never concatenate user input into SQL; never leak raw database errors or stack traces to callers. Use parameterized queries (SQLAlchemy does this for you) and translate low-level errors into safe, meaningful ones.

## Learning Objectives

By the end of this module, you can:

- Create and manage SQLAlchemy sessions correctly (open, use, commit/rollback, close).
- Perform CRUD: create, read, update, and delete `Task`/`Project` rows.
- Write queries with `select`, filtering, ordering, and relationship access.
- Use transactions and rollback to keep data consistent on failure.
- Handle database errors without leaking details.
- Avoid unsafe query patterns (no string-concatenated SQL).
- Write tests for the data-access layer using a test database and transaction rollback.

## Prerequisites

- Module 04 (models, engine, connection string), Module 03 (pytest), Module 02 (Python).
- A working Postgres database with the TaskFlow tables created.

## Key Concepts

### 1. Engine vs. session — and the unit of work

The **engine** (Module 04) manages connections. The **session** is your workspace for a unit of work: you add and modify objects, then `commit` to persist them or `rollback` to discard them. SQLAlchemy tracks your changes and writes them out as one consistent batch.

#### Suggested Visual

**Type:** Flowchart
**Purpose:** Make the session lifecycle concrete — the #1 confusion point.
**Placement:** Right after this paragraph.
**Caption:** *The session lifecycle: open → use → commit or rollback → close.*
**What to show:** A vertical flow: **Open session** → **Add/query/modify objects** → decision diamond **Success?** → on *yes* **commit()** → **close()**; on *no* **rollback()** → **close()**. Annotate that `close()` always runs (use a `with` block or `try/finally`), and that forgetting `commit()` silently discards changes.

### 2. Managing sessions safely

Use a context-managed session so it always closes:

```python
from sqlalchemy.orm import Session

def create_project(engine, name: str) -> int:
    with Session(engine) as session:
        project = Project(name=name)
        session.add(project)
        session.commit()          # persist; without this, nothing is saved
        return project.id
```

> **Callout — Forgetting `commit()` is the classic bug.** Your code runs, no error appears, but the data was never saved. The `with` block guarantees the session closes; *you* must remember to commit.

> **🧠 Remember:** `flush()` and `commit()` are not the same. `flush` sends your SQL to the database (so you can read back a generated `id`) but stays inside the open transaction; `commit` makes it permanent. A flush without a commit still vanishes on close — only `commit` durably saves.

### 3. CRUD with the data-access layer

A repository module wraps each operation in a small, testable function:

```python
from sqlalchemy import select

def create_task(session, title, project_id, priority="medium"):
    task = Task(title=title, project_id=project_id, priority=priority)
    session.add(task)
    session.commit()
    return task

def get_task(session, task_id):
    return session.get(Task, task_id)         # returns None if not found

def update_task(session, task_id, **changes):
    task = session.get(Task, task_id)
    if task is None:
        return None
    for field, value in changes.items():
        setattr(task, field, value)
    session.commit()
    return task

def delete_task(session, task_id):
    task = session.get(Task, task_id)
    if task is not None:
        session.delete(task)
        session.commit()
```

### 4. Queries: `select`, filtering, ordering, relationships

SQLAlchemy 2.x uses `select()`:

```python
from sqlalchemy import select

def list_tasks(session, *, only_open=False):
    stmt = select(Task)
    if only_open:
        stmt = stmt.where(Task.done == False)     # filtering
    stmt = stmt.order_by(Task.priority.desc())     # ordering
    return session.scalars(stmt).all()
```

> **Secure-coding callout — no string SQL.** Notice you never build a SQL string. `Task.done == False` becomes a *parameterized* query, which is immune to SQL injection. If you ever feel tempted to write `f"... WHERE title = '{user_input}'"`, stop — that's the classic injection vulnerability.

> **🏭 In production:** SQL injection has topped breach reports for two decades, and it almost always starts with one "harmless" f-string in a query. The ORM parameterizes values for you by default — the safe path is also the easy path, as long as you never hand-build SQL from user input.

Access related rows through the relationship:

```python
project = session.get(Project, 1)
for task in project.tasks:          # loads related tasks
    print(task.title)
```

### 5. Transactions: atomic, all-or-nothing

A transaction groups multiple changes so they succeed or fail *together*. If step two fails, `rollback` undoes step one, preventing half-written data:

```python
def move_task_to_project(session, task_id, new_project_id):
    try:
        task = session.get(Task, task_id)
        task.project_id = new_project_id
        # ... imagine another related change here ...
        session.commit()                 # both changes persist together
    except Exception:
        session.rollback()               # undo everything on failure
        raise
```

> **💡 Why this matters:** "All-or-nothing" is the whole point of a transaction. Without it, a failure halfway through a multi-step change leaves the database in a state that should never exist — a task moved but its counter not updated. `rollback` guarantees you never persist a half-truth.

### 6. Handling database errors safely

Catch SQLAlchemy errors and translate them — don't let raw DB messages reach the caller:

```python
from sqlalchemy.exc import IntegrityError

def create_project_safe(session, name):
    try:
        project = Project(name=name)
        session.add(project)
        session.commit()
        return project
    except IntegrityError:
        session.rollback()
        raise ValueError(f"A project named {name!r} already exists")  # safe message
```

> **Secure-coding callout — don't leak details.** A raw `IntegrityError` can expose table names and constraints. Translate it into a clean, safe message. In Module 06 this becomes a proper HTTP error response.

### 7. Testing database code

Test against a real (test) database, and roll back after each test so tests stay isolated:

```python
import pytest
from sqlalchemy.orm import Session

@pytest.fixture
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    sess = Session(bind=connection)
    yield sess
    sess.close()
    transaction.rollback()      # undo everything this test did
    connection.close()
```

Each test runs in its own transaction that is rolled back, so tests never pollute each other.

> **Callout — how the reference tests do it.** The companion suite `code/module-05-tests.py` applies this same isolation idea with a *fresh in-memory SQLite database per test*, so it runs without a PostgreSQL server. Same goal — perfectly isolated tests — with zero setup.

## Example Walkthrough

The companion files:

- `code/module-05-example.py` — a `repository` module with `create_task`, `get_task`, `list_tasks`, `update_task`, `delete_task`, a transaction example, and safe error handling.
- `code/module-05-starter.py` — repository functions with `TODO`s and **one intentional session bug** (a missing `commit`) for the Debug/Fix exercise.
- `code/module-05-tests.py` — pytest tests using the rollback-per-test session fixture.

Run the data layer and its tests:

```bash
python code/module-05-example.py     # exercises CRUD against Postgres
pytest code/module-05-tests.py -v    # runs the data-layer tests
```

## Common Mistakes or Misunderstandings

- **Forgetting `commit()`** — changes silently vanish.
- **Leaving sessions open** — use `with Session(engine) as session:` or `try/finally`.
- **Not rolling back on error** — leaves the session in a broken state.
- **Building SQL strings from user input** — SQL injection. Always use ORM/parameterized queries.
- **Leaking raw DB errors** — translate them into safe messages.
- **Tests that depend on each other** — use rollback-per-test isolation.

## Before You Start the Lab

In the lab you'll implement the TaskFlow repository, write a filtered/ordered query, wrap a multi-step operation in a transaction, fix a broken session, and test the data layer. Confirm the example runs and the tests pass first.

---

### Short Exercise 1 — Implement and verify `create`/`get`

- **Estimated Time:** 12 min
- **Goal:** Write your first two repository functions with correct session handling.
- **Starter Context:** `code/module-05-starter.py` with `create_task`/`get_task` `TODO`s.
- **Task Instructions:**
  1. Implement `create_task` (add, commit, return the task).
  2. Implement `get_task` using `session.get(Task, id)`.
  3. Create a task, then fetch it back by id and print it.
- **Success Criteria:** The fetched task matches what you created and persists across a fresh session.
- **Expected Result:** Re-opening a session and calling `get_task` returns the saved row.
- **Optional Hint:** If `get_task` returns `None`, you probably forgot to `commit` in `create_task`.
- **Key Takeaway:** Persistence only happens on `commit`. The "it ran but nothing saved" symptom almost always points to a missing commit.

---

### Short Exercise 2 — Write a filtered, ordered query

- **Estimated Time:** 12 min
- **Goal:** Use `select()` with `where` and `order_by` safely.
- **Starter Context:** Several tasks with mixed `done` and `priority` values.
- **Task Instructions:**
  1. Write `list_open_tasks(session)` returning tasks where `done == False`.
  2. Order results by `priority` descending.
  3. Print the titles.
- **Success Criteria:** Only open tasks return, highest priority first.
- **Expected Result:** Completed tasks are excluded; ordering is correct.
- **Optional Hint:** `session.scalars(stmt).all()` returns model objects.
- **Key Takeaway:** Building queries with the ORM keeps them readable *and* parameterized — you get safety against SQL injection for free, without ever writing raw SQL.

---

### Short Exercise 3 — Debug/Fix the broken session

- **Estimated Time:** 15 min
- **Goal:** Diagnose and fix the classic "no commit" session bug.
- **Starter Context:** The intentionally broken function in `code/module-05-starter.py`.
- **Task Instructions:**
  1. Run the related test and watch it fail (data not found).
  2. Trace the session lifecycle: open → add → ??? → close.
  3. Add the missing `commit()` and re-run.
- **Success Criteria:** The test passes; the row persists.
- **Expected Result:** A green test and a saved record after the fix.
- **Optional Hint:** Walk the lifecycle flowchart and find the missing step.
- **Key Takeaway:** Most session bugs are lifecycle bugs. Internalizing open → use → commit/rollback → close makes you debug them in seconds instead of hours.

---

## Using Claude Code in This Module

**When to use it:**
- **Diagnose** a session or transaction bug.
- **Explain** what a query will execute.
- **Review** error handling for leaks.

**Prompts to try:**
1. *"This repository function runs without error but the data isn't saved. Walk through the session lifecycle and tell me what's missing."*
2. *"Review this error handling. Does it leak any database details to the caller? Suggest a safe, generic message while preserving useful logging."*

> **Always validate.** After Claude Code proposes a fix, run the tests and confirm the data actually persists and rolls back as expected. Verify no raw `IntegrityError` text reaches the caller. Never paste real credentials into a prompt.

**If Claude Code is unavailable:** Use the session-lifecycle flowchart as a manual checklist and enable `echo=True` on the engine to read the actual SQL being run.

## Key Takeaways

- The session is your unit of work: open → use → commit/rollback → close.
- Forgetting `commit()` is the #1 silent bug; context-managed sessions prevent leaks.
- Use `select()` with `where`/`order_by`; the ORM keeps queries parameterized and injection-safe.
- Transactions make multi-step changes atomic; `rollback` recovers from failure.
- Translate DB errors into safe messages — never leak raw details.
- Test the data layer with rollback-per-test isolation.

**Next:** In **Module 06 — Flask REST API Development**, you'll expose this data layer over HTTP with validation, consistent JSON errors, and correct status codes.
