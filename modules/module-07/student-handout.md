# Module 07 — Final Backend Mini-Project (Capstone)

## Overview

This is where it all comes together. Over six modules you built TaskFlow layer by layer: clean Python utilities (M02), tests (M03), SQLAlchemy models on PostgreSQL (M04), a data-access layer (M05), and a Flask REST API (M06). The capstone integrates every layer into one complete, runnable, tested service — and then asks you to extend it with at least one new **end-to-end feature** that spans the model, data-access, API, and test layers.

This module is intentionally lighter on new concepts and heavier on **engineering judgment**: deciding where logic belongs, what to test first, and how to keep the contract consistent. You'll use Claude Code to plan and review like a senior teammate would — and validate everything yourself.

## Why This Matters

Real backend work is rarely a single new idea; it's *integration* — wiring known pieces into a coherent whole and extending it safely without breaking what exists. The ability to take a feature request, trace it through every layer, implement it cleanly, and prove it works with tests is exactly what early-career backend engineers are hired to do. This capstone is a rehearsal for the job.

## Learning Objectives

By the end of this module, you can:

- Assemble a layered backend (utilities → data access → API) into one runnable service.
- Add a new end-to-end feature spanning model, data-access, API, and tests.
- Write tests at the unit and API levels for new behavior.
- Apply validation, consistent errors, and correct status codes throughout.
- Use Claude Code to produce a safe implementation plan, review the code, and suggest tests — then validate everything manually.
- Run and demonstrate the full service from the command line.

## Prerequisites

- Modules 01–06 complete: project structure, Python, pytest, SQLAlchemy/Postgres, and the Flask API.
- A working Postgres database and your TaskFlow code from prior modules.

## Key Concepts

### 1. The end-to-end architecture

TaskFlow is a **layered** application. Each layer has one responsibility and talks only to its neighbors:

#### Suggested Visual

**Type:** Architecture Diagram
**Purpose:** Give learners the mental map of the whole system before they extend it.
**Placement:** Right after this paragraph.
**Caption:** *TaskFlow's layered architecture — a request flows down and a response flows back up.*
**What to show:** Vertical stack of boxes:
**HTTP Client (curl/tests)** → **Flask API layer — routes, validation, status codes (M06)** → **Data-access layer — repository, sessions, transactions (M05)** → **SQLAlchemy models (M04)** → **PostgreSQL**.
Side annotations: utilities (`taskutils`, M02) feed the API/data layers; pytest (M03) tests every layer. Arrows point both directions to show request-down, response-up.

| Layer | Responsibility | Built in |
|---|---|---|
| API (routes) | parse, validate, status codes, JSON | M06 |
| Data access (repository) | sessions, queries, transactions | M05 |
| Models | schema, relationships, constraints | M04 |
| Utilities | pure logic (slug, priority score) | M02 |
| Tests | prove every layer works | M03 |

> **💡 Why this matters:** Layers aren't bureaucracy — they're what makes the system testable. Because the repository doesn't know about HTTP and the routes don't know about SQL, you can unit-test data logic without a web server and test routes without a real database. Tangle the layers and every test suddenly needs the whole stack.

### 2. Delivering a feature across layers

A new feature is a vertical slice. For example, **"complete a task"** touches:

```text
Model (M04):        Task already has a `done` boolean — no change needed
Data access (M05):  add complete_task(session, task_id) -> Task | None
API (M06):          POST /api/v1/tasks/<id>/complete -> 200 / 404
Tests (M03):        unit test for complete_task + API test for the route
```

Or **"filter tasks by status"**:

```text
Data access (M05):  list_tasks(session, status="open") with a where-clause
API (M06):          GET /api/v1/tasks?status=open -> 200 (validate the param)
Tests:              unit test the filter + API test the query param + 422 for bad status
```

> **Callout — Where does logic belong?** Validation lives at the API boundary; data rules and queries live in the data-access layer; persistence/relationships live in the models. Keeping each concern in its home layer is the central decision you'll practice today.

### 3. Test strategy across levels

For each new feature, write at least:

- **Unit tests** for the data-access function (using the rollback-per-test session fixture from M05).
- **API tests** with the Flask test client (success, not-found, and validation cases).

### 4. Reinforced: validation, safe errors, status codes

The capstone is also a security and contract review. Every new endpoint must:

- Validate input server-side (return `422` on bad values, `400` on malformed JSON).
- Return correct status codes (`200`/`201`/`404`).
- Never leak stack traces or DB details (generic `500` via the error handler).
- Never build SQL from user input (use the ORM).

> **Secure-coding callout:** A new feature is a new attack surface. Re-apply every habit — `.env` for secrets, server-side validation, parameterized queries, safe errors — to the code you add today.

## Example Walkthrough

The companion files:

- `code/module-07-example.py` — a reference integrated TaskFlow service (app factory wiring utilities + repository + API) plus a documented new feature: `GET /api/v1/tasks?status=open` filtering and a `POST /api/v1/tasks/<id>/complete` action.
- `code/module-07-starter.py` — a wired-but-incomplete service with `TODO`s marking the capstone feature to implement.
- `code/module-07-tests.py` — a pytest suite covering the integrated service and the new feature (unit + API tests).

Run the full stack and the tests:

```bash
# 1. Ensure Postgres is running and .env has DATABASE_URL
export FLASK_APP=app
flask run

# 2. In another terminal, exercise the new feature:
curl "http://127.0.0.1:5000/api/v1/tasks?status=open"
curl -X POST http://127.0.0.1:5000/api/v1/tasks/1/complete

# 3. Run the full test suite (unit + API):
pytest -v
pytest --cov=app --cov-report=term-missing   # coverage across the service
```

A recommended approach for your capstone feature:

```text
1. Plan the vertical slice: which layers change?
2. Data layer first: implement + unit-test the repository function.
3. API next: add the route, validation, and status codes.
4. API tests: success, not-found, invalid input.
5. Harden: check errors don't leak; confirm correct codes.
6. Demo: run flask + curl; read the responses.
```

> **🏭 In production:** "Demo it and read the status codes aloud" isn't busywork — it's the cheapest integration test there is. Running the real stack end-to-end catches the wiring bugs that unit tests miss: a route pointed at the wrong function, a stale server, a `200` that should've been a `404`.

## Common Mistakes or Misunderstandings

- **Putting business logic in the route.** Keep it in the data layer; routes stay thin.
- **Skipping the unit test "because the API test covers it."** Both levels catch different bugs.
- **Forgetting validation on the new endpoint.** New surface, same rules.
- **Returning `200` for "not found"** on the new route. Use `404`.
- **Implementing everything before testing anything.** Build and test the slice incrementally.
- **Accepting Claude Code's plan without reading it.** You own the design.

## Before You Start the Lab

In the lab you'll run the full stack, implement the new feature end-to-end, add tests, harden validation/errors, and demo the API. Confirm now that the example service runs (`flask run`), `pytest` is green, and `curl` reaches your endpoints.

---

### Short Exercise 1 — Trace a feature through the layers

- **Estimated Time:** 12 min
- **Goal:** Plan a vertical slice before writing code.
- **Starter Context:** The feature "count tasks per project."
- **Task Instructions:**
  1. On paper or in a comment, list which layers change (model? data access? API? tests?).
  2. Define the data-access function signature.
  3. Define the API route, method, path, and success status code.
  4. List the tests you'd write.
- **Success Criteria:** A clear, layer-by-layer plan with signatures and a status code.
- **Expected Result:** A short written plan you could hand to a teammate.
- **Optional Hint:** Counting is a read — likely a new repository query + a `GET` route.
- **Key Takeaway:** Strong engineers design the slice before coding. Knowing where each concern lives prevents tangled logic and rework.

---

### Short Exercise 2 — Implement the data layer + unit test first

- **Estimated Time:** 15 min
- **Goal:** Build and prove the feature's core logic before the API.
- **Starter Context:** `code/module-07-starter.py` with the repository `TODO`.
- **Task Instructions:**
  1. Implement the repository function for your feature (e.g., `complete_task` or `list_tasks(status=...)`).
  2. Write a unit test using the rollback-per-test session fixture.
  3. Run `pytest -v` for just that test.
- **Success Criteria:** The data-layer function works and its unit test passes in isolation.
- **Expected Result:** A green unit test proving the core behavior before any HTTP is involved.
- **Optional Hint:** Test the not-found / empty case too, not just the happy path.
- **Key Takeaway:** Building the data layer first, with tests, gives you a trustworthy foundation — so when the API misbehaves later, you know the bug is in the route, not the logic.

---

### Short Exercise 3 — Expose and API-test the feature

- **Estimated Time:** 15 min
- **Goal:** Wire the route and prove the full slice end-to-end.
- **Starter Context:** Your tested repository function and the API `TODO`.
- **Task Instructions:**
  1. Add the route (correct method, path, validation, status codes).
  2. Write Flask test-client tests: success, not-found (`404`), and invalid input (`422`).
  3. Run the feature via `curl`, then run the API tests.
- **Success Criteria:** The endpoint returns correct codes for all three cases; tests pass.
- **Expected Result:** A working, tested endpoint demonstrable with `curl`.
- **Optional Hint:** Validate any query param or path id before calling the repository.
- **Key Takeaway:** A feature isn't "done" until it's correct at the HTTP boundary *and* proven by tests at both levels — that's the definition of shippable backend work.

---

## Capstone Decision Points

As you build, you'll hit real ambiguity. Make deliberate choices:

- **Where does validation go?** (API layer — before the repository.)
- **One query or filter in Python?** (Prefer a filtered DB query — let Postgres do the work.)
- **What status code for an invalid `?status=` value?** (`422` — well-formed request, bad value.)
- **What to test first?** (The data layer, then the API.)
- **How much to add?** (One solid, tested feature beats three half-finished ones.)

## Using Claude Code in This Module

**When to use it:**
- **Plan** a safe implementation before coding.
- **Review** your integrated code for missing validation, leaks, and wrong status codes.
- **Suggest** additional test cases across layers.

**Prompts to try:**
1. *"Here's the feature I want to add: [describe it]. Give me a safe, layer-by-layer implementation plan (model → repository → route → tests). Don't write the code yet — I'll implement it."*
2. *"Review my new endpoint and repository function for missing validation, leaked errors, wrong status codes, and untested edge cases. List issues in priority order."*

> **Always validate.** Read the plan critically and reject steps that put logic in the wrong layer. Run every suggested test and confirm it protects real behavior. You are the engineer of record — Claude Code advises, you decide.

> **🧠 Remember:** Claude Code can write a function, but it can't own the *architecture* — it doesn't carry the pager when the layers tangle six months from now. Where logic lives, what the contract promises, and which trade-off to accept are judgment calls that stay yours.

**If Claude Code is unavailable:** Use the layered-architecture diagram and the decision-points list as your own planning checklist, and review your slice against the "Common Mistakes" list.

## Final Integration Checklist

Before you call the capstone done, confirm:

- [ ] The full service runs with `flask run` against PostgreSQL.
- [ ] The new feature works end-to-end (verified with `curl`).
- [ ] Unit tests cover the new data-access logic.
- [ ] API tests cover success, not-found (`404`), and invalid input (`422`/`400`).
- [ ] All endpoints return correct status codes.
- [ ] Input is validated server-side; no client-trust shortcuts.
- [ ] Errors return safe, generic JSON — no stack traces or DB details.
- [ ] No raw/concatenated SQL; credentials only in `.env`.
- [ ] `pytest` is green and coverage is meaningful (not just high).
- [ ] You can demo the API and explain each response and status code.

## Key Takeaways

- A backend is layers with clear responsibilities; features are vertical slices through them.
- Build and test the data layer first, then expose and API-test it.
- Reapply every habit to new code: validation, safe errors, correct codes, secrets hygiene.
- Test at both unit and API levels — each catches different bugs.
- Claude Code plans and reviews; you make the engineering decisions and validate the result.

**You did it.** TaskFlow is now a complete, tested, secure, database-backed REST API — built the way professional backend teams build software. Carry these habits — structure, testing, safe persistence, contract-driven APIs, and supervised AI assistance — into your first engineering role.
