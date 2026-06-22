# Module 07 Lab — Capstone: Ship a New TaskFlow Feature End-to-End

## Overview

This is the capstone. You'll run the full TaskFlow stack — utilities, data layer, models, Postgres, and the Flask API — as one service, then extend it with a new **end-to-end feature** that spans the data-access layer, the API, and tests. You'll plan the vertical slice, build the data layer first, expose it over HTTP, test at both levels, harden validation and errors, and demo the running API.

This module is light on new concepts and heavy on engineering judgment: deciding where logic lives, what to test first, and how to keep the contract consistent.

## Learning Objectives

By the end of this lab you will be able to:

- Run the integrated TaskFlow service end-to-end.
- Plan and implement a feature as a vertical slice (data access → API → tests).
- Write unit and API tests for new behavior.
- Apply validation, safe errors, and correct status codes throughout.
- Use Claude Code to plan and review, then validate everything yourself.

## Prerequisites

- Modules 01–06 complete: project structure, Python, pytest, SQLAlchemy/Postgres, Flask API.
- A working database and your TaskFlow code from prior modules.

## Estimated Time

~3+ hours (capstone). Short challenge exercises are embedded in the build.

## Environment and Setup

```bash
cd taskflow
source .venv/bin/activate
psql "$DATABASE_URL" -c "SELECT 1;"     # DB reachable
export FLASK_APP=app
git checkout -b feature/capstone
```

Confirm the existing service runs and is green before adding anything:
```bash
flask run            # serves on http://127.0.0.1:5000
pytest -v            # existing suite passes
```

Companion code files (generated separately):

- `code/module-07-example.py` — a reference integrated service with the new feature implemented.
- `code/module-07-starter.py` — a wired-but-incomplete service with `TODO`s marking the capstone feature.
- `code/module-07-tests.py` — unit + API tests for the integrated service and the new feature.

## Scenario

TaskFlow works, but the team needs two capabilities before launch: clients must be able to **filter tasks by status** and **mark a task complete**. You're the engineer assigned the feature. Take the request, trace it through the layers, implement it cleanly, prove it with tests, and demo it.

The capstone feature:
- `GET /api/v1/tasks?status=open` — filter tasks by status (validate the param).
- `POST /api/v1/tasks/<id>/complete` — mark a task done (`200` / `404`).

## Tasks

### Task 1: Plan the vertical slice

#### 🔍 Think First (do not skip)
On paper or in a comment block, plan **both** features layer by layer before writing any code:

- Which layers change for `GET /tasks?status=open`? (Likely data access + API + tests — not the model.)
- Which layers change for `POST /tasks/<id>/complete`? (The `Task.done` boolean already exists.)
- For an invalid `?status=` value, which status code is correct — `400`, `404`, or `422`? Justify it.
- What's the data-access function signature for each? What's the route signature?
- What tests will you write at each level?

#### Checkpoint
A short, written, layer-by-layer plan for both features that you could hand to a teammate.

#### Expected Output
A plan like:
```text
list_tasks(session, status=None) -> filtered query
  GET /api/v1/tasks?status=open  -> 200; invalid status -> 422
complete_task(session, task_id) -> Task | None
  POST /api/v1/tasks/<id>/complete -> 200; missing -> 404
Tests: unit (data layer) + API (success/404/422)
```

> **💡 Why this matters:** Planning the slice before coding is how you avoid putting validation in the repository or a query in the route. Five minutes naming which layer changes saves an hour of untangling logic that ended up in the wrong place.

---

### Task 2: Build the data layer first (with unit tests)

#### Goal
Implement and prove the feature's core logic before any HTTP.

#### 🧠 Your Turn
Open `code/module-07-starter.py` and implement the repository functions yourself:

- **Goal:** Implement `list_tasks(session, status=None)` (filter by status when provided) and `complete_task(session, task_id)` (set `done=True`, commit, return the task; return `None` if missing).
- **Constraints:** Build the query conditionally; commit on changes; handle the not-found case; no raw SQL.
- **Expected outcome:** `complete_task` on a real id returns a task with `done=True`; on a missing id returns `None`.

Then write unit tests using the rollback-per-test session fixture from Module 05. Cover the happy path **and** the not-found/empty case.

#### Steps
1. Implement the two functions in `app/repository.py`.
2. Write unit tests in your test file.
3. Run just those tests:
   ```bash
   pytest -v -k "complete_task or list_tasks"
   ```

#### Checkpoint
The data-layer functions work and their unit tests pass in isolation.

#### Expected Output
```text
test_complete_task_sets_done PASSED
test_complete_task_missing_returns_none PASSED
test_list_tasks_filters_by_status PASSED

3 passed
```

**Hint:** For `list_tasks`, start from `select(Task)` and add a `.where(...)` only when `status` is provided.

---

### Task 3: Expose and API-test the feature

#### Goal
Wire the routes and prove the full slice end-to-end.

#### 🧠 Your Turn
Add the routes yourself:

- **Goal:** Add `GET /api/v1/tasks` honoring an optional `?status=` query param, and `POST /api/v1/tasks/<int:task_id>/complete`.
- **Constraints:** Validate the `status` param against allowed values (`422` on bad value); return `404` when completing a missing task; keep routes thin.
- **Expected outcome:** `?status=open` returns only open tasks (`200`); `?status=banana` returns `422`; completing a missing id returns `404`.

#### Steps
1. Add the routes to `app/routes.py`.
2. Write Flask test-client tests: success, not-found (`404`), invalid status (`422`).
3. Demo with curl, then run the tests:
   ```bash
   flask run
   # another terminal:
   curl -i "http://127.0.0.1:5000/api/v1/tasks?status=open"
   curl -i -X POST http://127.0.0.1:5000/api/v1/tasks/1/complete
   curl -i "http://127.0.0.1:5000/api/v1/tasks?status=banana"   # expect 422
   pytest -v
   ```

#### Checkpoint
The endpoints return correct codes for all cases; tests pass.

#### Expected Output
```text
HTTP/1.1 200 OK            # ?status=open
HTTP/1.1 200 OK            # POST .../1/complete  (task now done)
HTTP/1.1 422 UNPROCESSABLE ENTITY   # ?status=banana
```

**Hint:** Validate the `status` param *before* calling the repository.

---

### Task 4: Harden and demo

#### Goal
Confirm the new surface is safe and the whole service runs.

#### Steps
1. Trigger errors and confirm no stack trace or DB text leaks.
2. Confirm credentials are only in `.env` and no raw SQL was introduced.
3. Run the full suite with coverage:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```
4. Demo: `flask run`, then walk through each `curl` and read the responses/status codes aloud.

#### Checkpoint
Full suite green; new feature demoable; no leaks.

#### Expected Output
```text
==== N passed ====
app/...   XX%   (coverage meaningful, not just high)
```

---

## ⚠️ Open Challenge — One filter or many?

The product team hints they'll soon want to filter by `status` **and** `project_id` **and** `priority`.

- **The ambiguity:** You could add separate functions per filter, one function with many optional params, or a flexible filter object. Each trades simplicity against future flexibility.
- **Your task:** Choose an approach for `list_tasks`, implement it, and write 3–4 sentences defending it against over-engineering vs. premature rigidity. Decide: do you build for today's two filters or tomorrow's five?
- **Success criteria:** A working, tested implementation plus a clear, defensible justification.

No single right answer — make the call an engineer would and own it.

---

## 🧩 Debug / Fix — The filter that ignores its argument

In `code/module-07-starter.py`, the `list_tasks` `TODO` (or a planted version) builds the query but never applies the `status` filter — it returns *all* tasks regardless of the parameter.

- **Symptom:** `GET /tasks?status=open` returns completed tasks too; the unit test for filtering fails.
- **Likely cause:** The `.where(...)` clause is missing or not reassigned (`stmt = stmt.where(...)`), so the filter is silently dropped.
- **Your task:** Fix the query so the filter is actually applied, and confirm the failing test goes green.

**Success criteria:** `?status=open` excludes done tasks and the filter unit test passes.

**Hint:** `select()` is immutable per call — you must reassign `stmt = stmt.where(...)`, not just call it.

> **🧠 Remember:** `stmt.where(...)` returns a *new* statement; it doesn't modify `stmt` in place. A filter that's built but never reassigned is silently dropped — the query runs fine and returns wrong data, which is exactly why only a real assertion (not "it ran") catches it.

---

## 🧪 Experiment — Change a status code on purpose

- **Goal:** Feel why the contract matters.
- **Steps:**
  1. Temporarily make `POST .../complete` return `200` for a missing task instead of `404`.
  2. Run the API tests — watch the not-found test fail.
  3. Revert to `404`.
- **Ask yourself:** What would a client that relies on `404` do if you shipped the `200` version?

**Key observation to record:** A wrong status code is a silently broken contract — tests catch it before clients do.

> **🏭 In production:** Shipping `200` where a `404` belongs doesn't fail in *your* code — it fails in everyone *downstream*: retry logic that never retries, dashboards that miscount, a frontend that shows "saved" when nothing was. Contract bugs blast outward; that's why a single status-code test is worth so much.

---

## Short Challenge Exercises

### Exercise A — Plan "count tasks per project"

- **Estimated Time:** 12 min
- **Goal:** Practice slicing a feature before coding.
- **Starter Context:** The feature "count tasks per project."
- **Task Instructions:**
  1. List which layers change (model? data access? API? tests?).
  2. Define the repository function signature and the API route + success code.
  3. List the tests you'd write.
- **Success Criteria:** A clear, layer-by-layer plan with signatures and a status code.
- **Expected Result:** A short plan you could hand to a teammate.
- **Optional Hint:** Counting is a read — a new query plus a `GET` route.
- **Key Takeaway:** Strong engineers design the slice before coding; knowing where each concern lives prevents tangled logic and rework.

### Exercise B — Unit-test the not-found path

- **Estimated Time:** 12 min
- **Goal:** Prove `complete_task` handles a missing id.
- **Starter Context:** Your `complete_task` from Task 2.
- **Task Instructions:**
  1. Call `complete_task(session, 999999)` on an empty/rolled-back DB.
  2. Assert it returns `None`.
  3. Confirm no exception is raised.
- **Success Criteria:** The not-found unit test passes.
- **Expected Result:** `1 passed`; `None` returned, no crash.
- **Optional Hint:** `session.get(Task, id)` returns `None` when absent.
- **Key Takeaway:** The happy path is only half the story — testing the not-found case is what makes the `404` route trustworthy.

### Exercise C — API-test the invalid query param

- **Estimated Time:** 13 min
- **Goal:** Pin the `422` contract for `?status=`.
- **Starter Context:** Your `GET /tasks` route.
- **Task Instructions:**
  1. Write a Flask test-client test for `?status=banana`.
  2. Assert the status code is `422`.
  3. Assert the response JSON names the invalid field.
- **Success Criteria:** The test passes and documents the validation contract.
- **Expected Result:** `1 passed`; `422` with a helpful error body.
- **Optional Hint:** Validate the param in the route before querying.
- **Key Takeaway:** Validating query params at the boundary keeps bad input out of the data layer and gives clients a clear, correct `422`.

---

## Final Integration Checklist

Before you call the capstone done, confirm:

- [ ] The full service runs with `flask run` against PostgreSQL.
- [ ] The new feature works end-to-end (verified with `curl`).
- [ ] Unit tests cover the new data-access logic (happy + not-found).
- [ ] API tests cover success, not-found (`404`), and invalid input (`422`).
- [ ] All endpoints return correct status codes.
- [ ] Input is validated server-side; no client-trust shortcuts.
- [ ] Errors return safe, generic JSON — no stack traces or DB details.
- [ ] No raw/concatenated SQL; credentials only in `.env`.
- [ ] `pytest` is green and coverage is meaningful (not just high).
- [ ] You can demo the API and explain each response and status code.

**Definition of Done:** Commit your feature on `feature/capstone` and open a merge request whose description walks through the feature, the layers it touched, and the tests proving it works. This MR is your capstone deliverable.

## Validation / Success Criteria

You are done when every box in the Final Integration Checklist is checked and the merge request is open.

## Troubleshooting

- **Symptom:** `?status=open` returns done tasks.
  **Likely cause:** The `.where(...)` clause isn't reassigned.
  **Fix:** `stmt = stmt.where(Task.done == False)`.

- **Symptom:** `POST .../complete` returns `200` for a missing task.
  **Likely cause:** Not mapping a `None` repository result to `404`.
  **Fix:** If `complete_task` returns `None`, return `404`.

- **Symptom:** Coverage is high but bugs slip through.
  **Likely cause:** Tests execute lines without asserting behavior.
  **Fix:** Add meaningful assertions, especially on the not-found/invalid paths.

- **Symptom:** Full suite passes locally but the feature fails via curl.
  **Likely cause:** The running server uses a different DB or stale code.
  **Fix:** Restart `flask run`; confirm `DATABASE_URL` matches.

- **Symptom:** Tests pollute each other.
  **Likely cause:** Not using rollback-per-test isolation.
  **Fix:** Reuse the Module 05 session fixture.

## Stretch Goal / Extension

Add a second feature slice of your own choosing (e.g., `GET /api/v1/projects/<id>/tasks` or a task count per project), fully tested at both levels. One solid, tested feature beats three half-finished ones — only take this on after the core capstone is green.

## Using Claude Code in This Lab

Ask Claude Code to plan before you code, then critique the plan:
> *"Here's the feature I want to add: filter tasks by status and complete a task. Give me a safe, layer-by-layer implementation plan (model → repository → route → tests). Don't write the code yet — I'll implement it."*

And to review when done:
> *"Review my new endpoint and repository function for missing validation, leaked errors, wrong status codes, and untested edge cases. List issues in priority order."*

**Required manual verification:** Read the plan critically and reject any step that puts logic in the wrong layer (e.g., validation in the repository). Run every suggested test and confirm it protects real behavior. You are the engineer of record — Claude Code advises, you decide.

**No-AI fallback:** Use the layered-architecture map and the capstone decision points as your own planning checklist, and review your slice against the Final Integration Checklist.

## Key Takeaways

- A backend is layers with clear responsibilities; features are vertical slices through them.
- Build and test the data layer first, then expose and API-test it.
- Reapply every habit to new code: validation, safe errors, correct codes, secrets hygiene.
- Test at both unit and API levels — each catches different bugs.
- A wrong status code is a broken contract; tests catch it before clients do.
- Claude Code plans and reviews; you make the engineering decisions and validate the result.
