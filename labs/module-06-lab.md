# Module 06 Lab — Build the TaskFlow REST API with Flask

## Overview

TaskFlow becomes a real service. In this lab you build a Flask 3.x REST API on top of your Module 05 repository: an application factory, a `tasks` blueprint under `/api/v1`, CRUD routes returning JSON, server-side validation, correct HTTP status codes, and error handlers that never leak stack traces. You'll write API tests with the Flask test client, fix a route that wrongly returns `200` on validation failure, and decide where a piece of logic belongs.

## Learning Objectives

By the end of this lab you will be able to:

- Structure a Flask app with an application factory and a blueprint.
- Build GET/POST/PUT/DELETE routes returning JSON.
- Validate request bodies server-side and return correct status codes (200/201/400/404/422/500).
- Implement error handlers that don't leak internals.
- Integrate routes with the SQLAlchemy data layer (thin routes).
- Test endpoints with the Flask test client.

## Prerequisites

- Module 05 complete: `app/repository.py`, working Postgres, models.
- Modules 03–04 (pytest, models).

## Estimated Time

~75 minutes (core path). Short challenge exercises add ~40 minutes.

## Environment and Setup

```bash
cd taskflow
source .venv/bin/activate
pip install flask
pip freeze > requirements.txt
git checkout -b feature/api
```

Companion code files (generated separately):

- `code/module-06-example.py` — reference app factory + `tasks` blueprint (CRUD, validation, error handlers).
- `code/module-06-starter.py` — partial routes with `TODO`s, including **one route that returns `200` on validation failure**.
- `code/module-06-tests.py` — Flask test-client tests (success, 400, 404, 422).

## Scenario

Other systems — and a future frontend — will talk to TaskFlow over HTTP. They depend on your status codes and JSON shapes being correct and consistent. You're designing the contract: the API is a promise, and a wrong status code or a leaked stack trace is a broken (and insecure) promise.

## Tasks

### Task 1: Create the application factory and blueprint

#### Goal
Wire a minimal Flask app with a versioned `tasks` blueprint.

#### Steps
1. In `app/routes.py`:
   ```python
   from flask import Blueprint, request, jsonify
   from sqlalchemy.orm import Session
   from app.db import engine
   from app import repository

   tasks_bp = Blueprint("tasks", __name__)


   def serialize(task):
       return {"id": task.id, "title": task.title,
               "priority": task.priority, "done": task.done,
               "project_id": task.project_id}
   ```
2. In `app/__init__.py`:
   ```python
   from flask import Flask
   from app.routes import tasks_bp


   def create_app(config=None):
       app = Flask(__name__)
       if config:
           app.config.update(config)
       app.register_blueprint(tasks_bp, url_prefix="/api/v1")
       return app
   ```
3. Run it:
   ```bash
   export FLASK_APP=app
   flask run
   ```

#### Checkpoint
`flask run` starts and serves on `http://127.0.0.1:5000`.

#### Expected Output
```text
 * Running on http://127.0.0.1:5000
```

---

### Task 2: GET routes with correct status codes

#### Goal
List tasks and fetch one, returning `200` or `404`.

#### 🔍 Think First (do not skip)
- When a client requests `GET /tasks/9999` and no such task exists, which status code is correct — `200`, `404`, or `500`? Why?
- What's the difference a client experiences between `404` (missing) and `500` (broken)?

> **💡 Why this matters:** `404` says "you asked for something that doesn't exist" — the client's problem; `500` says "I broke" — your problem. Mixing them up sends clients (and on-call engineers) chasing the wrong bug at 3 a.m.

#### Steps
1. Add to `app/routes.py`:
   ```python
   @tasks_bp.get("/tasks")
   def get_tasks():
       with Session(engine) as session:
           tasks = repository.list_open_tasks(session)
           return jsonify([serialize(t) for t in tasks]), 200


   @tasks_bp.get("/tasks/<int:task_id>")
   def get_one(task_id):
       with Session(engine) as session:
           task = repository.get_task(session, task_id)
           if task is None:
               return jsonify({"error": "Task not found"}), 404
           return jsonify(serialize(task)), 200
   ```
2. Test with curl:
   ```bash
   curl -i http://127.0.0.1:5000/api/v1/tasks
   curl -i http://127.0.0.1:5000/api/v1/tasks/9999    # expect 404
   ```

#### Checkpoint
Existing id → `200`; unknown id → `404`.

#### Expected Output
```text
HTTP/1.1 404 NOT FOUND
{"error": "Task not found"}
```

---

### Task 3: POST with server-side validation

#### Goal
Create a task, returning `201` on success and `422` on invalid input.

#### Steps
1. Add a validator and the route:
   ```python
   def validate_task_payload(data):
       errors = {}
       if not (data or {}).get("title", "").strip():
           errors["title"] = "is required"
       if (data or {}).get("priority") not in {None, "low", "medium", "high"}:
           errors["priority"] = "must be low, medium, or high"
       return errors


   @tasks_bp.post("/tasks")
   def create():
       data = request.get_json(silent=True)
       if data is None:
           return jsonify({"error": "Malformed JSON"}), 400
       errors = validate_task_payload(data)
       if errors:
           return jsonify({"errors": errors}), 422
       with Session(engine) as session:
           task = repository.create_task(
               session, title=data["title"].strip(),
               project_id=data["project_id"],
               priority=data.get("priority", "medium"))
           return jsonify(serialize(task)), 201
   ```
2. Test:
   ```bash
   curl -i -X POST http://127.0.0.1:5000/api/v1/tasks \
        -H "Content-Type: application/json" \
        -d '{"title": "Ship release", "project_id": 1}'
   curl -i -X POST http://127.0.0.1:5000/api/v1/tasks \
        -H "Content-Type: application/json" -d '{}'      # expect 422
   ```

#### Checkpoint
Valid body → `201` + created task; empty body → `422` + field errors.

#### Expected Output
```text
HTTP/1.1 201 CREATED
{"id": 4, "title": "Ship release", "priority": "medium", "done": false, "project_id": 1}

HTTP/1.1 422 UNPROCESSABLE ENTITY
{"errors": {"title": "is required"}}
```

---

### Task 4: Error handlers that don't leak

#### Goal
Return safe, generic JSON on errors — never a stack trace.

#### Steps
1. In `app/__init__.py`, register handlers inside `create_app`:
   ```python
   @app.errorhandler(404)
   def handle_404(err):
       return jsonify({"error": "Resource not found"}), 404

   @app.errorhandler(500)
   def handle_500(err):
       app.logger.exception("Unhandled error")
       return jsonify({"error": "Internal server error"}), 500
   ```
2. Trigger an error and confirm the response body is generic.

#### Checkpoint
Errors return a generic JSON message; details appear only in server logs.

#### Expected Output
```text
HTTP/1.1 500 INTERNAL SERVER ERROR
{"error": "Internal server error"}
```

---

### Task 5: API tests with the Flask test client

#### Goal
Prove the contract with automated tests.

#### Steps
1. The reference suite `code/module-06-tests.py` already covers success, 400,
   404, and 422 against an in-memory database. Run it first, then add your own
   tests for the routes you built using the same test-client pattern:
   ```python
   import pytest
   from app import create_app

   @pytest.fixture
   def client():
       app = create_app({"TESTING": True})
       return app.test_client()

   def test_create_task_returns_201(client):
       resp = client.post("/api/v1/tasks",
                          json={"title": "Write tests", "project_id": 1})
       assert resp.status_code == 201

   def test_create_task_missing_title_returns_422(client):
       resp = client.post("/api/v1/tasks", json={})
       assert resp.status_code == 422
   ```
2. Run the reference suite:
   ```bash
   pytest code/module-06-tests.py -v
   ```

#### Checkpoint
The reference suite covers success, not-found, malformed, and validation cases and passes.

#### Expected Output
```text
test_create_task_returns_201 PASSED
test_create_task_missing_title_returns_422 PASSED
test_create_task_malformed_json_returns_400 PASSED
test_invalid_priority_returns_422 PASSED
test_get_missing_task_returns_404 PASSED
test_list_and_get_roundtrip PASSED
test_update_and_delete PASSED

7 passed
```

---

## 🧠 Your Turn — Implement PUT and DELETE

Round out CRUD for the API.

- **Goal:** Add `PUT /tasks/<int:task_id>` (update, `200` on success, `404` if missing, `422` on invalid fields) and `DELETE /tasks/<int:task_id>` (`204` on success, `404` if missing).
- **Constraints:** Routes stay thin — validate, delegate to the repository, shape the response. No business logic in the route.
- **Expected outcome:** Updating a missing id returns `404`; a successful delete returns `204` with an empty body.

**Hint:** `repository.update_task` returns `None` when the id doesn't exist — map that to `404`.

Design it yourself — no full solution here.

---

## 🧩 Debug / Fix — The 200-on-failure route

Open `code/module-06-starter.py`. One route validates input but returns `200` even when validation fails.

- **Symptom:** `curl -i` shows `HTTP/1.1 200 OK` with an error message in the body when you send an empty title.
- **Likely cause:** The route builds an error response but returns the default `200`, or returns the error dict without a status code.
- **Your task:** Make it return `422` (invalid values) or `400` (malformed JSON) as appropriate, and add a `500` handler so unexpected errors don't leak a stack trace.

**Success criteria:** Invalid input returns the correct code; no response body contains a stack trace or DB text.

**Hint:** A Flask route returns `(body, status_code)`. A bare `return jsonify(...)` defaults to `200`.

> **🧠 Remember:** A missing status code isn't "no answer" — it's a confident, wrong `200`. The most dangerous API bugs aren't crashes; they're successful-looking responses that quietly lie about what happened.

---

## ⚠️ Open Challenge — Route or helper?

The "serialize a task to JSON" logic and the "validate the payload" logic could live inline in each route, in module-level helpers, or in the data layer.

- **The ambiguity:** Inline is simple but duplicated; helpers are reusable but add indirection; pushing validation into the data layer blurs the HTTP boundary.
- **Your task:** Decide where `serialize` and `validate_task_payload` belong, implement it consistently, and write 2–3 sentences justifying the decision against duplication, testability, and layer responsibility.
- **Success criteria:** A consistent placement plus a clear, defensible justification.

There's no single correct answer — argue yours like an engineer.

---

## 🧪 Experiment — Status codes by method

- **Goal:** Feel how method + outcome maps to status code.
- **Steps:**
  1. `curl -i` a successful `POST` (note `201`), a successful `GET` (note `200`), and a `DELETE` (note `204`).
  2. Now `GET` a missing id (`404`) and `POST` an empty body (`422`).
  3. Build a small table of method → outcome → code from what you observed.
- **Ask yourself:** Why is `201` (not `200`) right for creation, and `422` (not `400`) right for valid JSON with bad values?

**Key observation to record:** The status code communicates *what happened* — it's the contract, not decoration.

> **⚖️ Tradeoff:** `204 No Content` on a successful DELETE says "done, nothing to return" — leaner than `200` with an empty body. The distinction is small, but consistent, conventional codes are what let a client write one handler that works across every endpoint.

---

## Short Challenge Exercises

### Exercise A — Distinguish 400 from 422

- **Estimated Time:** 12 min
- **Goal:** Return the right code for malformed vs. invalid.
- **Starter Context:** Your `POST /tasks` route.
- **Task Instructions:**
  1. Send genuinely malformed JSON (`-d 'not json'`) and return `400`.
  2. Send well-formed JSON with a bad `priority` and return `422`.
  3. Confirm each with `curl -i`.
- **Success Criteria:** Malformed → `400`; valid-but-wrong-values → `422`.
- **Expected Result:** Two different codes for two different failures.
- **Optional Hint:** `request.get_json(silent=True)` returns `None` for malformed JSON.
- **Key Takeaway:** `400` means "I couldn't parse this"; `422` means "I parsed it but the values are wrong." Clients rely on the distinction.

### Exercise B — Confirm no stack-trace leak

- **Estimated Time:** 12 min
- **Goal:** Verify error responses are safe.
- **Starter Context:** Your `500` handler.
- **Task Instructions:**
  1. Force an internal error (e.g., a bad `project_id` causing a DB error).
  2. Inspect the response body with `curl -i`.
  3. Confirm it's a generic message and that details are in the server log instead.
- **Success Criteria:** No stack trace or DB text in the response.
- **Expected Result:** `{"error": "Internal server error"}` with details only in logs.
- **Optional Hint:** Use `app.logger.exception(...)` to log server-side.
- **Key Takeaway:** Leaking internals is a security vulnerability — log details server-side, return generic messages to clients.

### Exercise C — Test the 404 path

- **Estimated Time:** 12 min
- **Goal:** Add an API test for a missing resource.
- **Starter Context:** `code/module-06-tests.py`.
- **Task Instructions:**
  1. Write a test that `GET`s a non-existent task id.
  2. Assert the status code is `404`.
  3. Assert the JSON has an `error` key.
- **Success Criteria:** The test passes and documents the not-found contract.
- **Expected Result:** `1 passed` for the new test.
- **Optional Hint:** Use a clearly non-existent id like `999999`.
- **Key Takeaway:** Tests pin the contract in place — a future refactor that breaks the `404` path fails loudly instead of silently.

---

## Validation / Success Criteria

You are done when:

- [ ] `flask run` serves the API and `curl` returns `201` for a valid POST.
- [ ] GET returns `200`/`404`; POST returns `201`/`422`/`400` correctly.
- [ ] PUT and DELETE are implemented with correct codes (🧠 Your Turn).
- [ ] The 200-on-failure route is fixed (🧩 Debug/Fix).
- [ ] Error handlers return generic JSON — no leaks.
- [ ] `pytest code/module-06-tests.py -v` is green.

**Definition of Done:** Commit `app/__init__.py`, `app/routes.py`, and your API tests on `feature/api` and open a merge request. Confirm in the description that all status codes are correct and no stack traces leak.

## Troubleshooting

- **Symptom:** `flask run` says "Could not locate a Flask application".
  **Likely cause:** `FLASK_APP` not set or no `create_app` found.
  **Fix:** `export FLASK_APP=app` and ensure `app/__init__.py` defines `create_app`.

- **Symptom:** POST returns `415 Unsupported Media Type`.
  **Likely cause:** Missing `Content-Type: application/json` header.
  **Fix:** Add `-H "Content-Type: application/json"` or use `client.post(..., json=...)`.

- **Symptom:** A validation failure returns `200`.
  **Likely cause:** Missing status code on the return.
  **Fix:** Return `(jsonify(...), 422)`.

- **Symptom:** Stack trace appears in the response.
  **Likely cause:** No error handler registered.
  **Fix:** Add `@app.errorhandler(500)` returning a generic message.

- **Symptom:** Routes 404 even though they exist.
  **Likely cause:** Forgot the `/api/v1` prefix.
  **Fix:** Call `/api/v1/tasks`, matching the blueprint prefix.

## Stretch Goal / Extension

Add a `GET /api/v1/health` endpoint returning `{"status": "ok"}` and `200`, and a test for it. Health checks are standard practice for any deployable service.

## Using Claude Code in This Lab

Ask Claude Code to review for leaks and missing validation:
> *"Review these Flask routes. Where am I missing server-side validation, and where could I be leaking stack traces or DB details? Suggest fixes."*

**Required manual verification:** Run the generated/changed tests and confirm each status code is actually returned. Manually trigger an error with `curl -i` and verify no internal details leak. Reject any test that asserts only `200`.

**No-AI fallback:** Use the status-code cheat sheet and review each route by hand with `curl -i`.

## Key Takeaways

- Structure with an app factory + blueprint; version routes under `/api/v1`.
- Return correct status codes — the contract clients depend on (`201`/`200`/`400`/`404`/`422`/`500`).
- Validate all input server-side; the browser is never a security boundary.
- Error handlers return safe, consistent JSON — never leak stack traces or DB details.
- Keep routes thin; delegate to the tested data layer.
- Test endpoints across success, missing, and invalid cases.
