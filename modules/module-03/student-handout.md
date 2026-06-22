# Module 03 — Unit Testing with pytest

## Overview

Professional engineers don't *hope* their code works — they *prove* it, and prove it keeps working as the codebase changes. In this module you write meaningful unit tests for your TaskFlow `taskutils` module using **pytest 8.x**. You'll apply the Arrange-Act-Assert pattern, cover happy-path, negative, edge, and boundary cases, use fixtures and parametrization, generate a coverage report, and — critically — learn to judge whether a test is actually *meaningful* or just decoration.

This is also where you learn a hard truth about AI: Claude Code can generate dozens of tests in seconds, and many of them will give you **false confidence**. Spotting shallow tests is a skill you'll practice deliberately.

## Why This Matters

Untested code is risky code. Every backend change — a new feature, a bug fix, a refactor — risks breaking something that used to work. Tests are the safety net that lets you change code *fearlessly*. From Day 2 onward, you'll test database code and APIs; the habits you build here are the foundation for all of it. A team that tests well ships faster, not slower, because they spend less time debugging regressions in production.

## Learning Objectives

By the end of this module, you can:

- Explain why unit testing matters and distinguish unit vs. integration vs. end-to-end tests.
- Write pytest tests using Arrange-Act-Assert and clear naming conventions.
- Write happy-path, negative, edge, and boundary tests, including testing that exceptions are raised.
- Use fixtures and `@pytest.mark.parametrize`.
- Run tests and generate a coverage report.
- Refactor code to be more testable and judge whether a test is meaningful.

## Prerequisites

- Module 02: the `taskutils`/`tasks` module with functions and a `Task` class to test against.
- An activated virtual environment.

## Key Concepts

### 1. Why test, and the test pyramid

The **test pyramid** describes a healthy balance:

```text
        /\        e2e        (few, slow, whole-system)
       /  \
      /----\      integration (some, medium, layers together)
     /      \
    /--------\    unit        (many, fast, one function/class)
```

- **Unit tests** check one function or class in isolation — fast and many.
- **Integration tests** check that layers work together (e.g., data access + database — Module 05).
- **End-to-end tests** drive the whole system (e.g., an HTTP request through the API — Module 06).

Today is all about the wide base: fast, focused unit tests.

### 2. Setup and your first test

```bash
pip install pytest pytest-cov
pip freeze > requirements.txt
```

pytest discovers files named `test_*.py` and functions named `test_*`. Write tests in `tests/`:

```python
# tests/test_taskutils.py
from app.taskutils import priority_score

def test_priority_score_high_returns_three():
    # Arrange
    priority = "high"
    # Act
    result = priority_score(priority)
    # Assert
    assert result == 3
```

Run it:

```bash
pytest                 # run all tests
pytest -v              # verbose: one line per test
pytest tests/test_taskutils.py::test_priority_score_high_returns_three  # one test
```

### 3. Arrange-Act-Assert and naming

**AAA** keeps tests readable: set up inputs (Arrange), run the code (Act), check the outcome (Assert). Name tests so a failure reads like a sentence: `test_<thing>_<condition>_<expected>`.

### 4. Happy-path, negative, edge, and boundary tests

One good function deserves several tests:

```python
import pytest
from app.taskutils import parse_task, InvalidTaskError

def test_parse_task_valid_returns_normalized():       # happy path
    assert parse_task({"title": " Ship "}) == {"title": "Ship", "priority": "medium", "done": False}

def test_parse_task_missing_title_raises():           # negative
    with pytest.raises(InvalidTaskError):
        parse_task({})

def test_parse_task_empty_title_raises():             # edge
    with pytest.raises(InvalidTaskError):
        parse_task({"title": "   "})
```

> **Callout — `pytest.raises` tests failure on purpose.** Verifying that bad input is *rejected* is just as important as verifying good input is accepted.

> **🧠 Remember:** Test *behavior*, not implementation. Assert what a function returns or raises — not how it computes it. A test that breaks when you harmlessly rename a private variable is testing the wrong thing, and it taxes every future refactor.

### 5. Fixtures: reusable setup

A **fixture** provides shared setup so tests stay DRY:

```python
import pytest

@pytest.fixture
def sample_tasks():
    return [
        {"title": "Deploy", "priority": "high"},
        {"title": "Docs", "priority": "low"},
    ]

def test_high_priority_filter(sample_tasks):
    result = high_priority_titles(sample_tasks)
    assert result == ["Deploy"]
```

### 6. Parametrization: many cases, one test

`@pytest.mark.parametrize` runs the same test logic over many inputs — perfect for boundary cases:

```python
@pytest.mark.parametrize("priority, expected", [
    ("low", 1),
    ("medium", 2),
    ("high", 3),
    ("unknown", 0),   # boundary / unexpected input
])
def test_priority_score_mapping(priority, expected):
    assert priority_score(priority) == expected
```

### 7. Coverage — a guide, not a goal

```bash
pytest --cov=app --cov-report=term-missing
```

This shows which lines ran during tests. **100% coverage does not mean bug-free** — it only means every line *executed*, not that every behavior was *checked*.

> **Callout — Coverage measures execution, not meaning.** A test with no meaningful `assert` can still raise coverage. Aim for meaningful assertions, not a number.

> **⚖️ Tradeoff:** Chasing a coverage *number* optimizes the wrong thing. 100% coverage with weak assertions gives false confidence; 80% that nails the tricky branches gives real safety. Coverage tells you what you *didn't* test — it can't tell you what you tested *well*.

## Example Walkthrough

The companion files work together:

- `code/module-03-example.py` — the TaskFlow functions under test.
- `code/module-03-tests.py` — a pytest suite demonstrating AAA, fixtures, parametrization, and `pytest.raises`.
- `code/module-03-starter.py` — functions with missing edge-case handling, used for the "fix the failing test" exercise.

Run the demonstration suite:

```bash
pytest code/module-03-tests.py -v
```

Then, in the starter, you'll find a test that *fails* because the function doesn't handle an edge case yet — your job is to fix the function, not the test.

## Common Mistakes or Misunderstandings

- **Tests with no real assertion** (or asserting `True`). They prove nothing.
- **Testing implementation, not behavior.** If a harmless refactor breaks your test, the test was too tightly coupled.
- **One giant test** that checks ten things. Prefer small, focused tests with clear names.
- **Chasing 100% coverage** instead of meaningful cases.
- **Trusting AI-generated tests blindly.** Read each one and ask: "What real behavior does this protect?"

## Before You Start the Lab

In the lab you'll write a meaningful test suite for `taskutils`: add edge and negative tests, fix a function so a failing test passes, parametrize boundary cases, and generate a coverage report. Make sure `pytest` runs cleanly from the project root first.

---

### Short Exercise 1 — Write the AAA trio

- **Estimated Time:** 12 min
- **Goal:** Cover one function with happy-path, negative, and edge tests.
- **Starter Context:** `parse_task` from Module 02 and an empty `tests/test_taskutils.py`.
- **Task Instructions:**
  1. Write a happy-path test for valid input.
  2. Write a negative test using `pytest.raises` for a missing title.
  3. Write an edge test for a whitespace-only title.
  4. Run `pytest -v`.
- **Success Criteria:** Three named tests pass; names read like sentences.
- **Expected Result:** `3 passed` with descriptive test names in verbose output.
- **Optional Hint:** Import `InvalidTaskError` alongside `parse_task`.
- **Key Takeaway:** A single function needs multiple tests because correct behavior includes *correctly rejecting* bad input. Negative tests are not optional.

---

### Short Exercise 2 — Parametrize boundary cases

- **Estimated Time:** 12 min
- **Goal:** Replace repetitive tests with one parametrized test.
- **Starter Context:** `priority_score` and any duplicated single-value tests.
- **Task Instructions:**
  1. Write one `@pytest.mark.parametrize` test covering `low`, `medium`, `high`, and an unknown value.
  2. Run `pytest -v` and note each case appears as its own line.
- **Success Criteria:** Four cases run from one test function; all pass.
- **Expected Result:** Four parametrized lines in verbose output.
- **Optional Hint:** The decorator's first arg is a comma-separated string of param names.
- **Key Takeaway:** Parametrization makes it cheap to test the *edges* (unknown/zero/boundary), which is exactly where bugs hide. Cheap-to-add tests get added.

---

### Short Exercise 3 — Fix the failing test (fix code, not the test)

- **Estimated Time:** 15 min
- **Goal:** Make a red test green by improving the function.
- **Starter Context:** `code/module-03-starter.py` with a function that mishandles an edge case and a test that fails because of it.
- **Task Instructions:**
  1. Run the suite and read the failure message.
  2. Identify the unhandled edge case in the function.
  3. Fix the **function** (do not weaken the test).
  4. Re-run until green.
- **Success Criteria:** The previously failing test passes without changing its assertions.
- **Expected Result:** A green suite and a more robust function.
- **Optional Hint:** Read the assertion and the actual vs. expected values in the failure output.
- **Key Takeaway:** A failing test is information, not an obstacle. The fix belongs in the code under test — weakening tests to get green is how bugs reach production.

---

## Using Claude Code in This Module

**When to use it:**
- **Generate** candidate tests and edge cases you might have missed.
- **Explain** a failing test's output.
- **Critique** whether a test is meaningful.

**Prompts to try:**
1. *"Suggest edge and boundary test cases for `parse_task` that I might be missing. List the cases and why each matters — don't write the full tests yet."*
2. *"Here is a failing pytest output. Explain why it fails and whether the bug is in the code or the test."*

> **Always validate.** Read every generated test and ask: *"What real behavior does this protect, and would it catch a genuine bug?"* Delete shallow tests (e.g., asserting a function "doesn't crash" with no outcome check). In the lab you'll critique an AI-generated shallow test together.

> **🏭 In production:** A test that can never fail is worse than no test — it shows green, lulls the team into trusting untested code, and quietly rots as the codebase changes. Ask of every test: "What change would make this go red?" If nothing would, delete it.

**If Claude Code is unavailable:** Use the four-category checklist — happy, negative, edge, boundary — to brainstorm cases by hand. The discipline is the value; AI just accelerates it.

## Key Takeaways

- Tests prove behavior and protect you during change; the unit base is wide and fast.
- Use AAA, clear names, and the four case types (happy/negative/edge/boundary).
- Fixtures reuse setup; parametrization covers many inputs cheaply.
- `pytest.raises` tests that bad input is rejected.
- Coverage guides you but doesn't prove correctness — meaningful assertions do.
- AI-generated tests need human review; shallow tests are worse than none.

**Next:** In **Module 04 — PostgreSQL Fundamentals & SQLAlchemy Models**, TaskFlow gains memory: you'll model `Task` and `Project` in a real database and connect to it from Python.
