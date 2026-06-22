# Module 05 Lab — Build the TaskFlow Data-Access Layer

## Overview

You have a schema; now you build the layer that *uses* it. In this lab you implement TaskFlow's **repository** (data-access layer): full CRUD with correctly managed SQLAlchemy sessions, a filtered and ordered query, and a multi-step operation wrapped in a transaction with rollback. You'll fix the classic "forgot to commit" session bug, handle database errors safely, and test the data layer with a rollback-per-test fixture.

The session lifecycle is the #1 source of database bugs — this lab makes it muscle memory.

## Learning Objectives

By the end of this lab you will be able to:

- Manage sessions correctly: open → use → commit/rollback → close.
- Implement CRUD repository functions for `Task` and `Project`.
- Write `select()` queries with filtering and ordering.
- Wrap a multi-step operation in a transaction and roll back on failure.
- Translate database errors into safe messages (no leaks).
- Test the data layer with a rollback-per-test session fixture.

## Prerequisites

- Module 04 complete: working Postgres, `app/models.py`, `app/db.py` with an engine.
- Modules 02–03 (Python, pytest).

## Estimated Time

~75 minutes (core path). Short challenge exercises add ~40 minutes.

## Environment and Setup

```bash
cd taskflow
source .venv/bin/activate
git checkout -b feature/repository
psql "$DATABASE_URL" -c "SELECT 1;"     # confirm DB is reachable
```

Companion code files (generated separately):

- `code/module-05-example.py` — reference repository (CRUD + transaction + safe errors).
- `code/module-05-starter.py` — repository `TODO`s with **one intentional missing-commit bug**.
- `code/module-05-tests.py` — pytest tests using the rollback-per-test fixture.

You'll build `app/repository.py`.

## Scenario

TaskFlow's API (Module 06) will sit directly on top of this layer. If the repository forgets to commit, leaks a raw DB error, or corrupts data on a half-finished update, the whole service is unreliable. You're building the dependable core.

## Tasks

### Task 1: Implement core CRUD

#### Goal
Write `create_task`, `get_task`, `update_task`, and `delete_task` with correct session handling.

#### 🔍 Think First (do not skip)
Trace the session lifecycle for a *create*:
- What three things must happen in order for a new task to persist?
- If `commit()` is missing, what does the caller see — an error, or silent data loss?
- Why does `with Session(engine) as session:` matter even if you remember to commit?

> **💡 Why this matters:** A session left open holds a database connection hostage. Under load, leaked sessions exhaust the connection pool and the whole service grinds to a halt — the `with` block is what guarantees the connection goes back, every time, even when an error is raised.

#### Steps
1. In `app/repository.py`:
   ```python
   from sqlalchemy import select
   from app.models import Task


   def create_task(session, title, project_id, priority="medium"):
       task = Task(title=title, project_id=project_id, priority=priority)
       session.add(task)
       session.commit()
       return task


   def get_task(session, task_id):
       return session.get(Task, task_id)        # None if not found


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
2. Exercise it from a script using a `with Session(engine) as session:` block.

#### Checkpoint
Create a task, then re-open a fresh session and `get_task` it back — it persists.

#### Expected Output
```text
Created: Task(id=1, title='Draft spec', done=False)
Refetched in new session: Task(id=1, title='Draft spec', done=False)
```

---

### Task 2: Write a filtered, ordered query

#### Goal
List only open tasks, highest priority first.

#### Steps
1. Add to `app/repository.py`:
   ```python
   def list_open_tasks(session):
       stmt = (
           select(Task)
           .where(Task.done == False)          # filtering
           .order_by(Task.priority.desc())      # ordering
       )
       return session.scalars(stmt).all()
   ```
2. Seed a few tasks with mixed `done`/`priority`, then call it.

#### Checkpoint
Completed tasks are excluded; results are ordered by priority.

#### Expected Output
```text
['Hotfix' (high), 'Review PR' (medium)]   # 'Archive old' (done) is excluded
```

> **Secure-coding note:** You never built a SQL string. `Task.done == False` becomes a *parameterized* query — immune to SQL injection. Never write `f"... WHERE title = '{user_input}'"`.

---

### Task 3: Wrap a multi-step operation in a transaction

#### Goal
Make a multi-step change atomic, with rollback on failure.

#### Steps
1. Add:
   ```python
   def move_task_to_project(session, task_id, new_project_id):
       try:
           task = session.get(Task, task_id)
           if task is None:
               raise ValueError("Task not found")
           task.project_id = new_project_id
           # imagine a second related change here that could fail
           session.commit()
           return task
       except Exception:
           session.rollback()       # undo everything on failure
           raise
   ```
2. Test the happy path, then force a failure (e.g., a non-existent project FK) and confirm nothing partial is saved.

#### Checkpoint
On failure, the task's `project_id` is unchanged (rollback worked).

#### Expected Output
```text
Before failure: project_id=1
After failed move: project_id=1   # rolled back, not partially applied
```

---

### Task 4: Test the data layer

#### Goal
Run the repository tests with rollback-per-test isolation.

#### Steps
1. Review the session fixture in `code/module-05-tests.py`. It spins up a fresh
   in-memory SQLite database per test (no PostgreSQL needed) and disposes it on
   teardown, so tests stay fully isolated:
   ```python
   @pytest.fixture
   def session():
       engine = create_engine(
           "sqlite://",
           connect_args={"check_same_thread": False},
           poolclass=StaticPool,
       )
       repo.create_all(engine)
       sess = Session(engine)
       try:
           yield sess
       finally:
           sess.rollback()      # discard anything uncommitted
           sess.close()
           engine.dispose()     # drop the in-memory database entirely
   ```
2. Run:
   ```bash
   pytest code/module-05-tests.py -v
   ```

#### Checkpoint
Tests pass and leave no shared state behind (each test gets its own database).

#### Expected Output
```text
test_create_and_get_task PASSED
test_get_task_missing_returns_none PASSED
test_list_tasks_only_open_excludes_done PASSED
test_update_task_changes_fields PASSED
test_update_task_missing_returns_none PASSED
test_delete_task_removes_row PASSED
test_create_project_safe_duplicate_raises_clean_error PASSED

7 passed
```

---

## 🧠 Your Turn — Add a safe `create_project`

The repository needs a way to create projects that handles duplicate names gracefully.

- **Goal:** Write `create_project_safe(session, name)` that creates a project, but on a duplicate-name `IntegrityError` rolls back and raises a clean `ValueError` (no raw DB text).
- **Constraints:** Catch `IntegrityError`, roll back, and raise a safe message; never leak constraint/table names.
- **Expected outcome:** A second project with the same name raises `ValueError("A project named 'Launch' already exists")`.

**Hint:** Import `IntegrityError` from `sqlalchemy.exc`; roll back *before* raising the safe error.

Design it yourself — no full solution here.

---

## 🧩 Debug / Fix — The silent missing commit

Open `code/module-05-starter.py`. One repository function adds a row but never commits.

- **Symptom:** A test fails because the data "isn't there" — `get_task` returns `None` right after a create, with no error raised.
- **Likely cause:** The function opens a session, adds the object, but never calls `commit()`; on close, the change is discarded.
- **Your task:** Trace the lifecycle (open → add → ??? → close), add the missing `commit()`, and re-run the test.

**Success criteria:** The test passes and the row persists across a fresh session.

**Hint:** "It ran but nothing saved" is almost always a missing commit.

> **🏭 In production:** This bug is dangerous because it's *silent* — no exception, no error log, just data that quietly never arrives. Users report "I saved it and it's gone," and you have nothing to grep for. Internalize the lifecycle so you spot the missing `commit()` on sight.

---

## ⚠️ Open Challenge — Where does the "move" validation belong?

`move_task_to_project` could validate that `new_project_id` actually exists *before* changing anything.

- **The ambiguity:** You could (a) check the project exists in the repository, (b) rely on the FK constraint to fail and roll back, or (c) leave validation to the API layer (Module 06).
- **Your task:** Pick one approach, implement it, and write 2–3 sentences justifying the trade-off (safety vs. duplication vs. layer responsibility).
- **Success criteria:** A working implementation plus a clear, defensible justification.

There is no single right answer — defend yours like an engineer.

---

## 🧪 Experiment — Watch the SQL

- **Goal:** See exactly what your queries execute.
- **Steps:**
  1. Temporarily set `echo=True` on the engine.
  2. Run `list_open_tasks` and read the echoed `SELECT ... WHERE tasks.done = false ORDER BY ...`.
  3. Note that your Python values appear as *bound parameters*, not inline string concatenation.
- **Ask yourself:** Where would an injection vulnerability have to live, and why can't it live here?

**Key observation to record:** The ORM parameterizes values automatically — that's why ORM queries are injection-safe by default.

> **🧠 Remember:** In a parameterized query the *value* and the *SQL structure* travel separately, so user input can never become executable SQL. That separation — not "escaping quotes" — is what actually closes the injection hole.

---

## Short Challenge Exercises

### Exercise A — Implement and verify `get` after `create`

- **Estimated Time:** 12 min
- **Goal:** Prove persistence across sessions.
- **Starter Context:** Your `create_task`/`get_task`.
- **Task Instructions:**
  1. Create a task in one `with Session(...)` block.
  2. Open a brand-new session and fetch it by id.
  3. Confirm the fields match.
- **Success Criteria:** The refetched task equals what you created.
- **Expected Result:** Same title, priority, and id in a fresh session.
- **Optional Hint:** If it returns `None`, you forgot to commit.
- **Key Takeaway:** Persistence happens only on `commit` — and a *new* session proves the data truly landed in the database.

### Exercise B — Update only the fields provided

- **Estimated Time:** 13 min
- **Goal:** Make `update_task` partial-update safe.
- **Starter Context:** `update_task(session, task_id, **changes)`.
- **Task Instructions:**
  1. Update only `priority` on an existing task.
  2. Confirm `title` and `done` are unchanged.
  3. Confirm updating a missing id returns `None`.
- **Success Criteria:** Only the passed field changes; missing id returns `None`.
- **Expected Result:** Untouched fields retain their values.
- **Optional Hint:** Iterate `changes.items()` and `setattr`.
- **Key Takeaway:** Partial updates keep the API flexible — callers change only what they mean to.

### Exercise C — Safe error message on duplicate

- **Estimated Time:** 13 min
- **Goal:** Confirm no DB internals leak.
- **Starter Context:** Your `create_project_safe` (🧠 Your Turn).
- **Task Instructions:**
  1. Insert a duplicate project name.
  2. Catch the resulting `ValueError` and print its message.
  3. Confirm the message contains no table/constraint names.
- **Success Criteria:** A friendly message, no raw `IntegrityError` text.
- **Expected Result:** `A project named 'Launch' already exists`.
- **Optional Hint:** Roll back before raising the safe error.
- **Key Takeaway:** Translating DB errors into safe messages prevents leaking internal structure — a habit that becomes a clean HTTP error in Module 06.

---

## Validation / Success Criteria

You are done when:

- [ ] CRUD functions persist and retrieve data across fresh sessions.
- [ ] `list_open_tasks` filters and orders correctly.
- [ ] `move_task_to_project` rolls back cleanly on failure.
- [ ] `create_project_safe` raises a safe `ValueError` on duplicates (🧠 Your Turn).
- [ ] The starter's missing-commit bug is fixed (🧩 Debug/Fix).
- [ ] `pytest code/module-05-tests.py -v` is green.

**Definition of Done:** Commit `app/repository.py` and your tests on `feature/repository` and open a merge request. Note that no raw SQL strings appear and errors don't leak DB details.

## Troubleshooting

- **Symptom:** Data "isn't saved" but no error appears.
  **Likely cause:** Missing `commit()`.
  **Fix:** Add `session.commit()` after `add`/`delete`/changes.

- **Symptom:** `InvalidRequestError: ... session is in a broken state`.
  **Likely cause:** An error occurred and you didn't roll back.
  **Fix:** `session.rollback()` in the `except` branch.

- **Symptom:** Tests pollute each other (data from one test affects another).
  **Likely cause:** Not using rollback-per-test isolation.
  **Fix:** Use the connection/transaction/rollback session fixture.

- **Symptom:** `IntegrityError` on insert with a bad `project_id`.
  **Likely cause:** Foreign key references a non-existent project.
  **Fix:** Insert the project first, or catch and translate the error.

## Stretch Goal / Extension

Add `list_tasks(session, *, status=None, project_id=None)` that optionally filters by status and/or project, building the `select()` conditionally. This previews the query-param filtering you'll expose over HTTP in Modules 06–07.

## Using Claude Code in This Lab

Ask Claude Code to diagnose the session bug, then verify:
> *"This repository function runs without error but the data isn't saved. Walk through the session lifecycle and tell me what's missing."*

**Required manual verification:** After applying any fix, run the tests and confirm the row both persists *and* rolls back as expected. Verify no raw `IntegrityError` text reaches the caller. Never paste real credentials into a prompt.

**No-AI fallback:** Use the session-lifecycle checklist (open → use → commit/rollback → close) and enable `echo=True` to read the real SQL.

## Key Takeaways

- The session is your unit of work: open → use → commit/rollback → close.
- Forgetting `commit()` is the #1 silent bug; context-managed sessions prevent leaks.
- Use `select()` with `where`/`order_by`; the ORM keeps queries parameterized and injection-safe.
- Transactions make multi-step changes atomic; `rollback` recovers from failure.
- Translate DB errors into safe messages — never leak raw details.
- Test the data layer with rollback-per-test isolation so tests never pollute each other.
