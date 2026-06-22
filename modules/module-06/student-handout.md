# Module 06 — Flask REST API Development

## Overview

TaskFlow becomes a real service. On top of your tested SQLAlchemy data-access layer (Module 05), you'll build a **Flask 3.x REST API**: a structured app using an application factory and blueprints, routes for each HTTP method, JSON request parsing and responses, server-side request validation, consistent error handling, and correct HTTP status codes. You'll also write API tests with Flask's test client and apply secure-coding practices throughout.

This is where all your earlier work pays off: clean Python, a tested data layer, and a real database now sit behind a clean HTTP contract that other programs (or a future frontend) can call.

## Why This Matters

An API is a **contract**. Other systems depend on your status codes, your JSON shapes, and your error responses being consistent and correct. Returning `200 OK` when validation failed, leaking a stack trace on error, or trusting client-side validation are real-world bugs that cause outages and security incidents. Designing the contract carefully — and validating every input on the server — is core backend engineering.

> **Secure-coding callouts (this module):** validate *all* input server-side (the browser is not a security boundary); never return raw SQL or stack traces; keep error responses generic but useful. The data layer already protects against SQL injection — your job here is the HTTP boundary.

## Learning Objectives

By the end of this module, you can:

- Structure a Flask app with an application factory and blueprints.
- Build routes for GET/POST/PUT/DELETE returning JSON.
- Parse and validate JSON request bodies server-side.
- Return consistent JSON responses and correct status codes (200/201/400/404/422/500).
- Implement error handlers that don't leak stack traces or database details.
- Integrate Flask with the SQLAlchemy data layer.
- Test endpoints with the Flask test client (success, invalid, missing-record, validation).

## Prerequisites

- Module 05 (data-access layer), Module 04 (models), Module 03 (pytest).
- Working Postgres and the TaskFlow repository code.

## Key Concepts

### 1. Request lifecycle and app structure

An HTTP request flows through your app in layers. Keeping those layers clean is what makes the service maintainable.

#### Suggested Visual

**Type:** Flowchart
**Purpose:** Show how an HTTP request travels through the Flask app to the database and back.
**Placement:** Right after this paragraph.
**Caption:** *An HTTP request's journey through TaskFlow.*
**What to show:** A horizontal flow: **Client (curl)** → **Flask route (blueprint)** → **Validate JSON input** → decision diamond **Valid?** → on *no* **400/422 JSON error**; on *yes* → **Repository / data layer (Module 05)** → **PostgreSQL** → **JSON response + status code** → back to **Client**. Annotate the validation step as "server-side — never trust the client."

### 2. The application factory and blueprints

An **application factory** is a function that builds and configures the app — making testing and configuration clean. **Blueprints** group related routes (all task routes together):

```python
# app/__init__.py
from flask import Flask
from app.routes import tasks_bp

def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.update(config)
    app.register_blueprint(tasks_bp, url_prefix="/api/v1")
    return app
```

> **Callout — `/api/v1` versioning.** Prefixing routes with a version lets you evolve the API later without breaking existing clients.

### 3. Routes, JSON, and status codes

Each route maps an HTTP method + path to a function that returns JSON and a status code:

```python
from flask import Blueprint, request, jsonify
from app.repository import create_task, get_task, list_tasks

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.get("/tasks")
def get_tasks():
    tasks = list_tasks()
    return jsonify([serialize(t) for t in tasks]), 200

@tasks_bp.get("/tasks/<int:task_id>")
def get_one(task_id):
    task = get_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(serialize(task)), 200

@tasks_bp.post("/tasks")
def create():
    data = request.get_json(silent=True)
    if not data or "title" not in data:
        return jsonify({"error": "Field 'title' is required"}), 422
    task = create_task(title=data["title"])
    return jsonify(serialize(task)), 201      # 201 Created
```

**Status code cheat sheet:**

| Code | Meaning | When |
|---|---|---|
| `200 OK` | success | a successful GET/PUT/DELETE |
| `201 Created` | resource created | a successful POST |
| `400 Bad Request` | malformed request | unparseable/invalid body shape |
| `404 Not Found` | resource missing | id doesn't exist |
| `422 Unprocessable Entity` | validation failed | well-formed JSON, bad values |
| `500 Internal Server Error` | unexpected failure | bug — return a *generic* message |

> **Callout — 201 vs 200, 400 vs 404 vs 422.** Use `201` for creation, `404` when the resource doesn't exist, and `422` when the JSON parsed fine but the *values* are invalid. These distinctions are the contract.

> **🧠 Remember:** A client reads your status code *before* it reads your body — often a machine does, with no human in the loop. Returning `200` with `{"error": ...}` tells every automated caller "success," and they'll happily process your error as data. The code is the contract; the body is just the details.

### 4. Server-side validation

Validate every incoming field on the server, regardless of any client checks:

```python
def validate_task_payload(data):
    errors = {}
    if not data.get("title", "").strip():
        errors["title"] = "is required"
    if data.get("priority") not in {None, "low", "medium", "high"}:
        errors["priority"] = "must be low, medium, or high"
    return errors
```

> **Secure-coding callout — the browser is not a security boundary.** Client-side validation improves UX but can be bypassed trivially (curl, Postman, a malicious client). The server must re-validate everything.

> **🏭 In production:** Every public endpoint is reachable by tools that never run your JavaScript — curl, scripts, bots, attackers. Treat client-side validation as a courtesy to honest users and server-side validation as the real gate. If only one can exist, it's the server's.

### 5. Consistent error handling — no leaks

Register error handlers so failures return clean JSON, never a stack trace:

```python
@app.errorhandler(500)
def handle_500(err):
    # log the real error server-side, return a safe message to the caller
    app.logger.exception("Unhandled error")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def handle_404(err):
    return jsonify({"error": "Resource not found"}), 404
```

> **Secure-coding callout — leaking is a vulnerability.** A stack trace or raw DB error in a response hands attackers your internal structure. Log details on the server; return a generic message to the client.

> **🧠 Remember:** A leaked stack trace is a free map for an attacker — it reveals your file paths, library versions, table names, and query shapes. Reconnaissance is the first step of an attack; don't ship the blueprint in your error responses.

### 6. Integrating with the data layer

Routes stay thin: they parse and validate input, call the Module 05 repository, and shape the response. Business and persistence logic stays in the data layer — not in the route.

### 7. Testing with the Flask test client

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    return app.test_client()

def test_create_task_returns_201(client):
    resp = client.post("/api/v1/tasks", json={"title": "Write tests"})
    assert resp.status_code == 201
    assert resp.get_json()["title"] == "Write tests"

def test_create_task_missing_title_returns_422(client):
    resp = client.post("/api/v1/tasks", json={})
    assert resp.status_code == 422
```

## Example Walkthrough

The companion files:

- `code/module-06-example.py` — a Flask app factory with a `tasks` blueprint exposing CRUD endpoints over the Module 05 repository, with JSON responses, validation, error handlers, and correct status codes.
- `code/module-06-starter.py` — partial routes with `TODO`s, including **one route that returns `200` even on validation failure** (the Debug/Fix).
- `code/module-06-tests.py` — pytest API tests using the Flask test client (success, 400, 404, 422 cases).

Run the API and try it:

```bash
pip install flask
export FLASK_APP=app
flask run                       # serves on http://127.0.0.1:5000

# In another terminal — exercise the endpoints with curl:
curl -X POST http://127.0.0.1:5000/api/v1/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Ship release"}'
curl http://127.0.0.1:5000/api/v1/tasks
curl http://127.0.0.1:5000/api/v1/tasks/9999   # expect 404

# Run the API tests:
pytest code/module-06-tests.py -v
```

## Common Mistakes or Misunderstandings

- **Returning `200` on failure.** Match the status code to what actually happened.
- **Trusting client-side validation.** Always re-validate on the server.
- **Leaking stack traces / DB errors.** Use error handlers and generic messages.
- **Fat routes.** Keep business logic in the data layer; routes parse, validate, delegate, respond.
- **Confusing 400 vs 422 vs 404.** Malformed vs. invalid-values vs. missing-resource.

## Before You Start the Lab

In the lab you'll implement CRUD routes, add request validation, return correct status codes, add error handlers, and write API tests. Confirm `flask run` serves the example and that a `curl` POST returns `201` first.

---

### Short Exercise 1 — Build a GET endpoint with correct codes

- **Estimated Time:** 12 min
- **Goal:** Return JSON with `200` for found and `404` for missing.
- **Starter Context:** `code/module-06-starter.py` with a `get_one` `TODO`.
- **Task Instructions:**
  1. Implement `GET /tasks/<int:task_id>`.
  2. Return `200` + the task JSON if found; `404` + an error JSON if not.
  3. Test both cases with `curl`.
- **Success Criteria:** Existing id → 200; unknown id → 404.
- **Expected Result:** `curl .../tasks/9999` returns a 404 JSON error.
- **Optional Hint:** `get_task` returns `None` when the row doesn't exist.
- **Key Takeaway:** Status codes *are* the API contract. A client distinguishes "missing" from "broken" entirely by the code you return.

---

### Short Exercise 2 — Validate a POST body server-side

- **Estimated Time:** 15 min
- **Goal:** Reject invalid input with `422` before touching the database.
- **Starter Context:** A `POST /tasks` route that currently accepts anything.
- **Task Instructions:**
  1. Parse JSON with `request.get_json(silent=True)`.
  2. Validate that `title` is present/non-empty and `priority` is allowed.
  3. Return `422` + field errors on failure; `201` + the created task on success.
- **Success Criteria:** Empty body → 422; valid body → 201.
- **Expected Result:** Validation errors come back as JSON with a `422` code; no bad rows are created.
- **Optional Hint:** Validate *before* calling the repository.
- **Key Takeaway:** Server-side validation is the real security and integrity boundary. Rejecting bad input early keeps the database clean and the API trustworthy.

---

### Short Exercise 3 — Debug/Fix the stack-trace leak

- **Estimated Time:** 12 min
- **Goal:** Stop the API from leaking internal details on error.
- **Starter Context:** A route that, on error, returns a raw exception/stack trace, and the starter's route that wrongly returns `200` on validation failure.
- **Task Instructions:**
  1. Trigger the error and observe the leaked details.
  2. Add a `500` error handler returning a generic JSON message; log the real error server-side.
  3. Fix the route that returns `200` on failure to return the correct code.
- **Success Criteria:** Errors return a generic message with the right status code; details appear only in server logs.
- **Expected Result:** No stack trace or DB text in any response body.
- **Optional Hint:** Use `app.errorhandler` and `app.logger.exception(...)`.
- **Key Takeaway:** Leaking internals is a security vulnerability, and a wrong status code is a broken contract. Safe, consistent error responses are non-negotiable in production APIs.

---

## Using Claude Code in This Module

**When to use it:**
- **Review** error handling for leaks and missing validation.
- **Generate** API test cases for edge conditions.
- **Explain** which status code fits a given scenario.

**Prompts to try:**
1. *"Review these Flask routes. Where am I missing server-side validation, and where could I be leaking stack traces or DB details? Suggest fixes."*
2. *"Generate Flask test-client tests for my `POST /api/v1/tasks` route covering success (201), missing title (422), and malformed JSON (400)."*

> **Always validate.** Run the generated tests and confirm each status code is actually returned. Manually trigger an error to verify no internal details leak. Don't accept a test that asserts only `200`.

**If Claude Code is unavailable:** Use the status-code cheat sheet and the request-lifecycle flowchart to review routes by hand, and exercise every endpoint with `curl`, checking the returned code with `curl -i`.

## Key Takeaways

- Structure with an app factory + blueprints; version routes under `/api/v1`.
- Return correct status codes — the contract clients depend on.
- Validate all input server-side; the browser is never a security boundary.
- Use error handlers to return safe, consistent JSON — never leak stack traces or DB details.
- Keep routes thin; delegate to the tested data layer.
- Test endpoints with the Flask test client across success, missing, and invalid cases.

**Next:** In **Module 07 — Final Backend Mini-Project**, you'll integrate every layer into one runnable, tested TaskFlow service and add a new end-to-end feature.
