# Module 02 — Python Fundamentals for Backend Development

## Overview

Now that TaskFlow has a clean home (Module 01) and you've built a working triage script in the Python Crash Lab (Modules 1.5–1.7), it's time to level up. This module is a fast, code-heavy tour of the Python features backend engineers reach for every single day: data types and collections, control flow, functions, modules and imports, error handling, file and environment handling, and a first taste of object-oriented programming. It assumes you're already comfortable with the basics from the bridge — variables, strings, conditionals, lists, dicts, loops, and simple functions — and pushes into the more idiomatic, applied patterns.

Every example is framed around real TaskFlow data — tasks, priorities, due dates — so these fundamentals feel like backend work, not toy syntax. The goal is **idiomatic, readable, single-responsibility code**, because in two modules you'll be testing this code, and in four modules it will be powering a live API.

## Why This Matters

Backend logic is mostly data transformation: take messy input, validate it, reshape it, and hand back something clean and predictable. The Python skills here are the vocabulary for that work. Writing them clearly — small functions, predictable inputs and outputs, no hidden surprises — is what makes the difference between code that's easy to test and secure later versus code that fights you at every step.

## Learning Objectives

By the end of this module, you can:

- Use Python data types and collections (lists, dicts, tuples, sets) to model task data.
- Write conditionals and loops idiomatically.
- Write clear functions with parameters, return values, and docstrings.
- Organize code into modules and import across files.
- Handle errors with `try`/`except`/`raise` and custom exceptions.
- Read and write files and read configuration from environment variables.
- Write a small class with `__init__`, methods, and a `__repr__`.

## Prerequisites

- Module 01: project skeleton, an activated virtual environment, and the Git workflow.
- Modules 1.5–1.7 (Python Crash Lab) — or equivalent comfort with variables, strings, conditionals, lists, dictionaries, loops, and simple functions.
- You can run `python` and `pytest`-style commands from the project root.

## Key Concepts

### 1. Types, truthiness, and collections

Backend code constantly decides "is this present and valid?" Python's **truthiness** rules power that:

```python
title = ""
if not title:            # empty string is falsy
    raise ValueError("Task title is required")
```

Choose the right collection for the job:

| Collection | Use when you need | TaskFlow example |
|---|---|---|
| `list` | ordered, changeable sequence | a list of tasks to process |
| `dict` | key → value lookup | a single task record |
| `tuple` | fixed, unchangeable group | `(2025, 12, 31)` for a date |
| `set` | unique membership tests | the allowed priority values |

```python
task = {"title": "Ship release", "priority": "high", "done": False}
allowed_priorities = {"low", "medium", "high"}   # set for fast membership
print(task["priority"] in allowed_priorities)    # True
```

> **🧠 Remember:** Truthiness is convenient but blunt: `0`, `""`, `[]`, and `None` are *all* falsy. `if not count:` treats a legitimate `0` like missing data — at a real boundary, prefer the explicit `if count is None:` when zero is a valid value.

### 2. Conditionals, loops, and comprehensions

Idiomatic Python favors comprehensions for simple transforms:

```python
tasks = [
    {"title": "A", "priority": "high"},
    {"title": "B", "priority": "low"},
]

# Filter to high-priority titles in one readable line
high = [t["title"] for t in tasks if t["priority"] == "high"]
```

> **Callout — Readability first.** A comprehension is great for a simple map/filter. If it grows nested or hard to read, use a regular loop. Clear beats clever.

### 3. Functions: parameters, returns, docstrings — and the mutable-default trap

Functions are the unit of backend logic. Write them small, named clearly, with a docstring:

```python
def priority_score(priority: str) -> int:
    """Return a numeric weight for sorting tasks by priority."""
    weights = {"low": 1, "medium": 2, "high": 3}
    return weights.get(priority, 0)
```

> **💡 Why this matters:** This function is trivial to test because it's *predictable* — same input, same output, no hidden state, no I/O. That property isn't an accident; it's the design goal. Functions that read files, hit the clock, or mutate globals are the ones that become painful to test in Module 03.

> **Callout — The mutable-default-argument trap.** This bug bites real backend code:

```python
# WRONG: the default list is created ONCE and shared across calls
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags

# RIGHT: use None as the sentinel
def add_tag(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

> **🏭 In production:** This bug is nasty precisely because it *passes the first test*. The shared list only corrupts on the second and third call, so it slips past quick manual checks and surfaces as data from one request bleeding into another — exactly the kind of intermittent bug that's miserable to reproduce.

### 4. Modules and imports

Code organized into modules is code you can reuse and test. Put related functions in `app/taskutils.py`, then import them:

```python
# app/taskutils.py
def normalize_title(title: str) -> str:
    return title.strip()

# elsewhere
from app.taskutils import normalize_title
```

### 5. Error handling: exceptions, `raise`, and custom exceptions

Validate at the boundary and fail loudly with meaningful errors. Python style favors **EAFP** ("easier to ask forgiveness than permission"):

```python
class InvalidTaskError(ValueError):
    """Raised when a task record is missing required fields."""

def parse_task(record: dict) -> dict:
    try:
        title = record["title"].strip()
    except KeyError:
        raise InvalidTaskError("Task is missing 'title'")
    if not title:
        raise InvalidTaskError("Task 'title' cannot be empty")
    return {"title": title}
```

> **Callout — Custom exceptions are documentation.** `InvalidTaskError` tells the next engineer (and the API in Module 06) exactly what went wrong and lets callers handle it precisely.

### 6. Files and environment variables

Reading config from the environment (not hardcoding it) is the same secrets discipline from Module 01:

```python
import os
from dotenv import load_dotenv

load_dotenv()                          # reads .env into the environment
db_url = os.environ.get("DATABASE_URL")  # None if not set — handle it
```

### 7. A first class

When data and the behavior that acts on it belong together, reach for a class:

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

A good `__repr__` makes debugging and test failures readable — you'll appreciate it in Module 03.

## Example Walkthrough

The companion file `code/module-02-example.py` is a `tasks` module that models and transforms TaskFlow task dictionaries and objects: filtering, sorting by priority, and a small `Task` class. Conceptually, the flow is:

```python
raw = [{"title": "Deploy", "priority": "high"}, {"title": "Docs", "priority": "low"}]

# 1. normalize/validate each record
# 2. sort by priority_score (high → low)
# 3. wrap into Task objects for the rest of the app to use
```

Run it from the project root:

```bash
python code/module-02-example.py
```

The companion `code/module-02-starter.py` contains function stubs with `TODO`s — these are what you'll complete in the short exercises and lab.

## Common Mistakes or Misunderstandings

- **Mutable default arguments.** Use `None` as the sentinel, never `[]` or `{}`.
- **Confusing falsy values.** `0`, `""`, `[]`, and `None` are all falsy — be explicit when it matters.
- **Functions that do too much.** Split anything that mixes parsing, validating, and formatting.
- **Silent failures.** Don't swallow exceptions with a bare `except: pass`; raise meaningful errors.
- **Hardcoding config.** Read it from the environment.

## Before You Start the Lab

In the lab you'll build a `taskutils` module: parse raw task records, validate fields, compute a priority score, and expose a small `Task` class. Make sure you can import across files (`from app.taskutils import ...`) and run a module from the project root.

---

### Short Exercise 1 — Model and filter task data

- **Estimated Time:** 12 min
- **Goal:** Use collections and a comprehension to transform TaskFlow data.
- **Starter Context:** A list of task dicts, each with `title` and `priority`.
- **Task Instructions:**
  1. Write `high_priority_titles(tasks)` returning a list of titles where `priority == "high"`.
  2. Use a list comprehension.
  3. Print the result for a sample list.
- **Success Criteria:** Given mixed priorities, only the high-priority titles are returned, in original order.
- **Expected Result:** e.g., `["Deploy", "Hotfix"]`.
- **Optional Hint:** `[t["title"] for t in tasks if ...]`.
- **Key Takeaway:** Most backend work is shaping collections of records. Choosing the right structure and a readable transform is the core daily skill.

---

### Short Exercise 2 — Fix the mutable-default bug

- **Estimated Time:** 10 min
- **Goal:** Recognize and fix a classic Python pitfall.
- **Starter Context:** A function `add_tag(tag, tags=[])` in `code/module-02-starter.py`.
- **Task Instructions:**
  1. Call `add_tag("urgent")` three times and observe the (buggy) shared list.
  2. Rewrite it using `tags=None` and the sentinel pattern.
  3. Re-run and confirm each call starts fresh.
- **Success Criteria:** Three independent calls each return a single-element list.
- **Expected Result:** `["urgent"]` every time, not `["urgent", "urgent", "urgent"]`.
- **Optional Hint:** The default value is created once, at function-definition time.
- **Key Takeaway:** Hidden shared state causes intermittent, hard-to-reproduce backend bugs. Predictable functions are testable functions — and testability is next module's whole focus.

---

### Short Exercise 3 — Validate with a custom exception

- **Estimated Time:** 15 min
- **Goal:** Practice boundary validation and meaningful errors.
- **Starter Context:** A `parse_task(record)` stub and an empty `InvalidTaskError`.
- **Task Instructions:**
  1. Define `InvalidTaskError(ValueError)`.
  2. In `parse_task`, raise it when `title` is missing or empty.
  3. Return a normalized dict on success.
  4. Try one valid and two invalid records.
- **Success Criteria:** Valid input returns a clean dict; invalid input raises `InvalidTaskError` with a clear message.
- **Expected Result:** Predictable success and predictable, descriptive failures.
- **Optional Hint:** `record.get("title", "").strip()` handles both missing and whitespace cases.
- **Key Takeaway:** Validating at the boundary with named exceptions is how backends stay trustworthy. In Module 06 these same errors become clean API responses instead of crashes.

---

## Using Claude Code in This Module

**When to use it:**
- **Explain** a confusing snippet (e.g., a dense comprehension).
- **Refactor** a long function into smaller single-responsibility pieces.
- **Spot** the mutable-default trap and other idiom issues.

**Prompts to try:**
1. *"Explain what this comprehension does and rewrite it as a plain loop so I can compare readability: `[t['title'] for t in tasks if t['priority']=='high']`."*
2. *"Review `parse_task` for edge cases I might have missed (missing keys, wrong types, empty strings). Suggest validations but don't rewrite the whole function."*

> **Always validate.** Run the code yourself. If Claude Code suggests an "improvement" that changes behavior, confirm it against your own test cases before accepting.

**If Claude Code is unavailable:** Use the Python docs and rubber-duck the snippet to a classmate. The skill is reasoning about inputs, outputs, and edge cases — AI just speeds it up.

## Key Takeaways

- Pick the right collection; lean on truthiness, but be explicit at boundaries.
- Write small, single-responsibility functions with docstrings and clear returns.
- Avoid the mutable-default trap with the `None` sentinel pattern.
- Organize code into importable modules.
- Validate input and raise meaningful, custom exceptions.
- Read config from the environment; bundle data + behavior in small classes.

**Next:** In **Module 03 — Unit Testing with pytest**, you'll prove this `taskutils` code works — and keeps working — with meaningful tests, fixtures, and parametrization.
