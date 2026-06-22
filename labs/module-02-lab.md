# Module 02 Lab — Build the `taskutils` Module

## Overview

TaskFlow has a clean home; now you fill it with logic. In this lab you build `app/taskutils.py`: functions that parse raw task records, validate fields, compute a priority score, and a small `Task` class that bundles data with behavior. You'll write idiomatic, single-responsibility Python — because in the next module you'll test every line of it.

You'll also hunt down the classic mutable-default-argument bug, a trap that bites real backend code.

## Learning Objectives

By the end of this lab you will be able to:

- Model task data with the right collections (dict, list, set).
- Write small, single-responsibility functions with clear inputs and outputs.
- Validate input at the boundary and raise meaningful custom exceptions.
- Avoid the mutable-default-argument trap.
- Write a small class with `__init__`, a method, and a `__repr__`.

## Prerequisites

- Module 01 complete: project skeleton, activated venv, Git workflow.
- You can import across files (`from app.taskutils import ...`) and run a module from the project root.

## Estimated Time

~60 minutes (core path). Short challenge exercises add ~35 minutes.

## Environment and Setup

```bash
cd taskflow
source .venv/bin/activate     # prompt shows (.venv)
git checkout -b feature/taskutils
```

Companion code files (generated separately):

- `code/module-02-starter.py` — function stubs with `TODO`s (including the mutable-default bug).
- `code/module-02-example.py` — a reference `tasks` module.

## Scenario

TaskFlow receives raw task records from a CSV import — messy dicts with stray whitespace, missing fields, and free-text priorities. Your job: build the `taskutils` module that turns that mess into clean, validated, sortable task data the rest of the app can trust.

## Tasks

### Task 1: Parse and validate a raw task record

#### Goal
Write `parse_task(record)` that normalizes a raw dict and rejects bad input.

#### 🔍 Think First (do not skip)
A raw record might look like any of these:
```python
{"title": " Ship release ", "priority": "HIGH"}
{"title": "", "priority": "low"}
{"priority": "medium"}            # no title at all
```
Before coding, answer:

- Which of these are valid? Which must be rejected, and with what error?
- Should `parse_task` *fix* a bad priority or *reject* it? (There's a defensible answer either way — decide and be consistent.)
- What should the return value look like so the rest of the app can rely on it?

#### Steps
1. In `app/taskutils.py`, define a custom exception:
   ```python
   class InvalidTaskError(ValueError):
       """Raised when a task record is missing required fields."""
   ```
2. Implement `parse_task`:
   ```python
   def parse_task(record: dict) -> dict:
       """Normalize a raw task record; raise InvalidTaskError on bad input."""
       title = record.get("title", "").strip()
       if not title:
           raise InvalidTaskError("Task 'title' is required")
       priority = record.get("priority", "medium").strip().lower()
       if priority not in {"low", "medium", "high"}:
           priority = "medium"
       return {"title": title, "priority": priority, "done": False}
   ```
3. Try it from a quick `__main__` block or the REPL.

#### Checkpoint
Valid input returns a clean dict; missing/empty title raises `InvalidTaskError`.

#### Expected Output
```text
{'title': 'Ship release', 'priority': 'high', 'done': False}
InvalidTaskError: Task 'title' is required
```

> **💡 Why this matters:** `parse_task` is the boundary where untrusted, messy input becomes clean data the rest of the app can trust. Validate once, here, and every downstream function can assume the data is good — instead of each one re-checking and re-guessing.

---

### Task 2: Compute a priority score

#### Goal
Write `priority_score(priority)` for sorting tasks.

#### Steps
1. Add the function:
   ```python
   def priority_score(priority: str) -> int:
       """Return a numeric weight for sorting tasks by priority."""
       weights = {"low": 1, "medium": 2, "high": 3}
       return weights.get(priority, 0)
   ```
2. Write `sort_tasks(tasks)` that returns tasks sorted by score, highest first:
   ```python
   def sort_tasks(tasks: list[dict]) -> list[dict]:
       """Return tasks ordered by priority, highest first."""
       return sorted(tasks, key=lambda t: priority_score(t["priority"]), reverse=True)
   ```

#### Checkpoint
A mixed list of tasks sorts high → low.

#### Expected Output
```text
[{'title': 'Hotfix', 'priority': 'high', ...},
 {'title': 'Docs', 'priority': 'medium', ...},
 {'title': 'Cleanup', 'priority': 'low', ...}]
```

---

### Task 3: Build the `Task` class

#### Goal
Bundle task data with behavior in a small class.

#### Steps
1. Add the class to `app/taskutils.py`:
   ```python
   class Task:
       def __init__(self, title: str, priority: str = "medium"):
           self.title = title
           self.priority = priority
           self.done = False

       def complete(self) -> None:
           self.done = True

       def __repr__(self) -> str:
           return f"Task(title={self.title!r}, priority={self.priority!r}, done={self.done})"
   ```
2. Create a `Task`, call `.complete()`, and print it.

#### Checkpoint
`__repr__` produces a readable, debuggable string and `done` flips to `True`.

#### Expected Output
```text
Task(title='Ship release', priority='high', done=False)
Task(title='Ship release', priority='high', done=True)
```

> **💡 Why this matters:** A good `__repr__` pays for itself the first time a test fails. `<Task object at 0x10f3a2b50>` tells you nothing; `Task(title='Ship release', priority='high', done=True)` tells you exactly what went wrong — you'll feel the difference in Module 03.

---

## 🧠 Your Turn — Add a filter helper

TaskFlow needs to list only the high-priority work.

- **Goal:** Write `high_priority_titles(tasks: list[dict]) -> list[str]` returning the titles of tasks where `priority == "high"`, in original order, using a list comprehension.
- **Constraints:** One readable line of logic; a docstring; no mutation of the input.
- **Expected outcome:** Given mixed priorities, returns e.g. `["Deploy", "Hotfix"]`.

**Hint:** `[t["title"] for t in tasks if ...]`.

Design it yourself — no full solution is provided here.

---

## 🧩 Debug / Fix — The mutable-default trap

Open `code/module-02-starter.py` and find:
```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags
```

- **Symptom:** Calling `add_tag("urgent")` three separate times returns `["urgent"]`, then `["urgent", "urgent"]`, then `["urgent", "urgent", "urgent"]`.
- **Likely cause:** The default `[]` is created **once** at function-definition time and shared across all calls.
- **Your task:** Rewrite it using the `None` sentinel pattern so each call starts fresh. Re-run three times to confirm.

**Success criteria:** Three independent calls each return a single-element list.

**Hint:** Default to `None`, then create a new list inside the function when it's `None`.

> **🧠 Remember:** The default value is evaluated *once*, when Python defines the function — not on each call. That single rule explains the entire bug, and it's why `None` plus "create it inside" is the only safe pattern for mutable defaults.

---

## Short Challenge Exercises

### Exercise A — Choose the right collection

- **Estimated Time:** 10 min
- **Goal:** Use a set for fast, correct membership checks.
- **Starter Context:** The `priority not in {...}` check from Task 1.
- **Task Instructions:**
  1. Define `ALLOWED_PRIORITIES = {"low", "medium", "high"}` at module level.
  2. Use it in `parse_task` instead of an inline set.
  3. Explain in a comment why a set (not a list) is the right choice here.
- **Success Criteria:** Validation still works; the allowed values are defined in one place.
- **Expected Result:** A single source of truth for allowed priorities.
- **Optional Hint:** Sets give O(1) membership and prevent duplicate values.
- **Key Takeaway:** Choosing the right collection makes intent clear and code correct — a set says "unique membership matters."

### Exercise B — Validate with a custom exception

- **Estimated Time:** 12 min
- **Goal:** Make failures predictable and descriptive.
- **Starter Context:** `parse_task` from Task 1.
- **Task Instructions:**
  1. Add a check that rejects a `title` longer than 200 characters with `InvalidTaskError`.
  2. Include the offending length in the message.
  3. Test one valid and one too-long title.
- **Success Criteria:** Over-long titles raise a clear `InvalidTaskError`; valid ones pass.
- **Expected Result:** A descriptive error like `Task 'title' too long (250 > 200)`.
- **Optional Hint:** `len(title)` after stripping.
- **Key Takeaway:** Boundary validation with named exceptions is how backends stay trustworthy — and these errors become clean API responses in Module 06.

### Exercise C — Read config from the environment

- **Estimated Time:** 12 min
- **Goal:** Avoid hardcoding configuration.
- **Starter Context:** Your `.env` from Module 01 with `DATABASE_URL`.
- **Task Instructions:**
  1. In a small script, `load_dotenv()` and read `os.environ.get("DATABASE_URL")`.
  2. Print whether it was found (don't print the value — it's a secret).
  3. Handle the `None` case gracefully.
- **Success Criteria:** The script reports "found" without printing the secret.
- **Expected Result:** `DATABASE_URL is configured` (or a safe "not set" message).
- **Optional Hint:** Use `python-dotenv` from Module 01; never print secret values.
- **Key Takeaway:** Configuration belongs in the environment, not the code — the same secrets discipline you started in Module 01.

---

## Validation / Success Criteria

You are done when:

- [ ] `parse_task` normalizes valid records and raises `InvalidTaskError` on bad input.
- [ ] `priority_score` and `sort_tasks` order tasks high → low.
- [ ] `high_priority_titles` works (🧠 Your Turn).
- [ ] `add_tag` is fixed with the `None` sentinel (🧩 Debug/Fix).
- [ ] The `Task` class has `__init__`, `complete()`, and a readable `__repr__`.
- [ ] `app/taskutils.py` imports cleanly from the project root.

**Definition of Done:** Commit `app/taskutils.py` on `feature/taskutils` and open a merge request. Briefly note in the description that the module is "designed to be testable" (it's the input to Module 03).

## Troubleshooting

- **Symptom:** `add_tag` keeps accumulating items across calls.
  **Likely cause:** Still using a mutable default.
  **Fix:** Default to `None` and create the list inside the function.

- **Symptom:** `from app.taskutils import ...` raises `ModuleNotFoundError`.
  **Likely cause:** Running from the wrong directory or missing `__init__.py`.
  **Fix:** Run from the project root; confirm `app/__init__.py` exists.

- **Symptom:** `parse_task` accepts an empty title.
  **Likely cause:** Checking `"title" in record` instead of the stripped value's truthiness.
  **Fix:** Strip first, then check `if not title`.

- **Symptom:** Sorting raises `KeyError: 'priority'`.
  **Likely cause:** A record was never normalized through `parse_task`.
  **Fix:** Parse records before sorting, or use `.get("priority", "medium")`.

## Stretch Goal / Extension

Add a `from_dict(cls, record)` classmethod to `Task` that calls `parse_task` and builds a `Task` from the normalized data — connecting your validation and your class in one clean entry point.

## Using Claude Code in This Lab

Ask Claude Code to review your `parse_task` for missed edge cases:
> *"Review `parse_task` for edge cases I might have missed (missing keys, wrong types, empty strings). Suggest validations but don't rewrite the whole function."*

**Required manual verification:** Run any suggested validation against your own examples before keeping it — confirm it doesn't change behavior for valid input.

**No-AI fallback:** Brainstorm edge cases by hand using the four categories you'll meet in Module 03 (happy, negative, edge, boundary).

## Key Takeaways

- Backend logic is mostly shaping and validating records — pick the right collection and keep functions small.
- Validate at the boundary and raise meaningful, custom exceptions.
- The mutable-default trap causes intermittent, hard-to-reproduce bugs; use the `None` sentinel.
- A small class with a good `__repr__` makes data and behavior travel together and debug cleanly.
- Predictable functions are testable functions — exactly what Module 03 needs.
