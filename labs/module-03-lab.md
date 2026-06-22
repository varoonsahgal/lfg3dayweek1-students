# Module 03 Lab — Test `taskutils` with pytest

## Overview

You wrote `taskutils` in Module 02; now you prove it works — and keeps working. In this lab you build a meaningful pytest suite: happy-path, negative, edge, and boundary tests, fixtures, parametrization, and a coverage report. You'll fix a function so a failing test passes (fixing the code, not the test), and you'll critique an AI-generated shallow test to learn the difference between coverage and confidence.

## Learning Objectives

By the end of this lab you will be able to:

- Write pytest tests using Arrange-Act-Assert and clear naming.
- Cover happy-path, negative, edge, and boundary cases, including `pytest.raises`.
- Use fixtures and `@pytest.mark.parametrize`.
- Generate and read a coverage report.
- Make a failing test pass by fixing the code under test.
- Judge whether a test is meaningful.

## Prerequisites

- Module 02 complete: `app/taskutils.py` with `parse_task`, `priority_score`, `sort_tasks`, `high_priority_titles`, and `Task`.
- Activated venv.

## Estimated Time

~60–75 minutes (core path). Short challenge exercises add ~35–40 minutes.

## Environment and Setup

```bash
cd taskflow
source .venv/bin/activate
pip install pytest pytest-cov
pip freeze > requirements.txt
git checkout -b feature/taskutils-tests
```

Companion code files (generated separately):

- `code/module-03-tests.py` — a reference suite (AAA, fixtures, parametrization, `pytest.raises`).
- `code/module-03-starter.py` — a function with a missing edge case and a failing test.
- `code/module-03-example.py` — functions under test.

You will write your own tests in `tests/test_taskutils.py`.

## Scenario

TaskFlow's `taskutils` module is about to be used by a database layer and an API. Before anyone builds on it, you make it trustworthy: a test suite that documents its behavior and catches regressions the moment they appear.

## Tasks

### Task 1: Write the Arrange-Act-Assert trio

#### Goal
Cover `parse_task` with happy-path, negative, and edge tests.

#### 🔍 Think First (do not skip)
For `parse_task`, list (on paper) at least one input for each category:

- **Happy path:** a valid record.
- **Negative:** input that should raise `InvalidTaskError`.
- **Edge:** a technically-valid-but-tricky input (e.g., whitespace-only title, mixed-case priority).
- **Boundary:** the smallest/largest acceptable input.

A function isn't "tested" until its *failure* behavior is verified too — which categories above test failure?

> **💡 Why this matters:** Most beginners test only the happy path and call it "done." But real input is hostile — empty, missing, malformed, oversized. The negative and boundary cases are exactly where production bugs live, so that's where your tests earn their keep.

#### Steps
1. Create `tests/test_taskutils.py`:
   ```python
   import pytest
   from app.taskutils import parse_task, InvalidTaskError


   def test_parse_task_valid_returns_normalized():
       # Arrange
       record = {"title": " Ship ", "priority": "HIGH"}
       # Act
       result = parse_task(record)
       # Assert
       assert result == {"title": "Ship", "priority": "high", "done": False}


   def test_parse_task_missing_title_raises():
       with pytest.raises(InvalidTaskError):
           parse_task({})


   def test_parse_task_whitespace_title_raises():
       with pytest.raises(InvalidTaskError):
           parse_task({"title": "   "})
   ```
2. Run:
   ```bash
   pytest -v
   ```

#### Checkpoint
Three named tests pass, and the names read like sentences in verbose output.

#### Expected Output
```text
tests/test_taskutils.py::test_parse_task_valid_returns_normalized PASSED
tests/test_taskutils.py::test_parse_task_missing_title_raises PASSED
tests/test_taskutils.py::test_parse_task_whitespace_title_raises PASSED

3 passed in 0.03s
```

---

### Task 2: Use a fixture for shared setup

#### Goal
Keep tests DRY with a reusable sample.

#### Steps
1. Add a fixture and a test that uses it:
   ```python
   @pytest.fixture
   def sample_tasks():
       return [
           {"title": "Deploy", "priority": "high", "done": False},
           {"title": "Docs", "priority": "low", "done": False},
       ]


   def test_high_priority_filter(sample_tasks):
       from app.taskutils import high_priority_titles
       assert high_priority_titles(sample_tasks) == ["Deploy"]
   ```
2. Run `pytest -v`.

#### Checkpoint
The fixture-backed test passes without duplicating setup data.

#### Expected Output
```text
tests/test_taskutils.py::test_high_priority_filter PASSED
```

---

### Task 3: Parametrize boundary cases

#### Goal
Cover many `priority_score` inputs from one test.

#### Steps
1. Add:
   ```python
   from app.taskutils import priority_score


   @pytest.mark.parametrize("priority, expected", [
       ("low", 1),
       ("medium", 2),
       ("high", 3),
       ("unknown", 0),   # boundary / unexpected input
   ])
   def test_priority_score_mapping(priority, expected):
       assert priority_score(priority) == expected
   ```
2. Run `pytest -v` and note each case appears as its own line.

#### Checkpoint
Four parametrized cases run and pass from one function.

#### Expected Output
```text
test_priority_score_mapping[low-1] PASSED
test_priority_score_mapping[medium-2] PASSED
test_priority_score_mapping[high-3] PASSED
test_priority_score_mapping[unknown-0] PASSED
```

---

### Task 4: Generate a coverage report

#### Goal
See which lines your tests execute.

#### Steps
1. Run:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```
2. Read the `Missing` column — those lines never ran.

#### Checkpoint
A coverage table prints with a percentage and a `Missing` column.

#### Expected Output
```text
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
app/taskutils.py        24      3    88%   31-33
--------------------------------------------------
TOTAL                   24      3    88%
```
(Numbers will differ.)

> Remember: coverage shows *execution*, not *correctness*. A line that ran is not the same as a behavior that was checked.

---

## 🧩 Debug / Fix — Make the failing test green (fix the code)

Open `code/module-03-starter.py` and run its bundled test:
```bash
pytest code/module-03-starter.py -v
```

- **Symptom:** A test fails because a function mishandles an edge case (e.g., a `None` or empty input it never anticipated).
- **Likely cause:** The function was written for the happy path only.
- **Your task:** Read the failure (actual vs. expected), identify the unhandled edge case, and fix the **function** — do **not** weaken the test's assertions.

**Success criteria:** The previously failing test passes without any change to its assertions.

**Hint:** The assertion message tells you exactly which input produced the wrong result.

> **💡 Why this matters:** Weakening a test to make it pass is the most expensive shortcut in software — it removes the alarm instead of fixing the fire. A red test is a bug caught early; "fix" it by changing the code, and the test keeps protecting you forever.

---

## 🧪 Experiment — Does coverage equal confidence?

- **Goal:** See why coverage can mislead.
- **Steps:**
  1. Write a "test" that calls `parse_task({"title": "X"})` but asserts nothing meaningful (e.g., `assert True`).
  2. Run coverage again — note the percentage may rise.
  3. Now ask: did that test protect any behavior? Delete it and replace it with a real assertion.
- **Ask yourself:** What changed in coverage? What *didn't* change in real safety?

**Key observation to record:** Coverage measured execution; only a meaningful assertion measures behavior.

> **🧠 Remember:** Coverage is a *map of what ran*, not a *verdict on what's correct*. It's great for finding untested code; it's useless for judging whether the tests you have actually check anything.

---

## 🧠 Your Turn — Parametrize the boundary cases yourself

Now you decide what to test. The guided tasks above gave you the patterns; here you design the coverage.

- **Goal:** Replace several near-duplicate `priority_score` tests with **one** parametrized test that pins down the boundaries.
- **Starter context:** `priority_score` maps each priority string to a number (e.g., `high` → 3, `medium` → 2, `low` → 1) and must handle an unknown/empty priority safely. You have the example functions in `code/module-03-example.py` and your own `app/taskutils.py`.
- **Your task:**
  1. Add a single test using `@pytest.mark.parametrize` that checks at least **four** `(priority, expected_score)` pairs: the highest, the lowest, a middle value, and one *boundary/odd* case (unknown priority, empty string, or mixed case like `"HIGH"`).
  2. Decide what the *correct* score for the odd case should be, then assert it — don't just assert it "doesn't crash."
  3. Run `pytest -v` and confirm each parametrized case shows as its own line.
- **Success criteria:** One parametrized test function produces four (or more) separately-reported passing cases, and at least one case is a deliberate boundary/odd input.
- **Expected result:**
  ```text
  tests/test_taskutils.py::test_priority_score[high-3] PASSED
  tests/test_taskutils.py::test_priority_score[low-1] PASSED
  tests/test_taskutils.py::test_priority_score[medium-2] PASSED
  tests/test_taskutils.py::test_priority_score[unknown-0] PASSED
  ```
  (Your IDs and the odd-case value will reflect your design choice.)
- **Optional hint:** `@pytest.mark.parametrize("priority, expected", [("high", 3), ...])` then take `priority` and `expected` as the test function's arguments.
- **Key Takeaway:** Good engineers don't just *follow* a test template — they *decide* what behavior matters and encode it. Parametrization turns a wall of copy-pasted tests into one readable table of behavior, and forcing yourself to name the "correct" answer for odd inputs is where you discover the spec was ambiguous all along.

---

## Short Challenge Exercises

### Exercise A — Test that `Task.complete()` works

- **Estimated Time:** 10 min
- **Goal:** Verify state change behavior on the class.
- **Starter Context:** The `Task` class from Module 02.
- **Task Instructions:**
  1. Arrange a `Task`, assert `done is False`.
  2. Act: call `.complete()`.
  3. Assert `done is True`.
- **Success Criteria:** One focused test passes.
- **Expected Result:** `1 passed` for the new test.
- **Optional Hint:** Use `is True` / `is False` for booleans.
- **Key Takeaway:** Behavior tests (state changed correctly) protect classes the same way they protect functions.

### Exercise B — Negative test for `sort_tasks`

- **Estimated Time:** 12 min
- **Goal:** Test behavior with awkward input.
- **Starter Context:** `sort_tasks` from Module 02.
- **Task Instructions:**
  1. Test that an empty list returns an empty list.
  2. Test that a single-task list returns that task unchanged.
  3. Test that ties keep a stable, predictable order.
- **Success Criteria:** All three tests pass and document the function's edges.
- **Expected Result:** `3 passed`.
- **Optional Hint:** Empty and single-element inputs are classic boundaries.
- **Key Takeaway:** The edges — empty, single, tied — are where bugs hide. Cheap-to-write edge tests catch expensive bugs.

### Exercise C — Critique an AI-generated test

- **Estimated Time:** 13 min
- **Goal:** Spot a shallow test.
- **Starter Context:** Ask Claude Code: *"Write a pytest test for `parse_task`."*
- **Task Instructions:**
  1. Read the generated test. Does it assert a real outcome, or just that the function "doesn't crash"?
  2. If shallow, rewrite it with a meaningful assertion.
  3. Write one sentence on what real behavior your version protects.
- **Success Criteria:** A meaningful test plus a one-sentence justification.
- **Expected Result:** A test that would actually catch a regression.
- **Optional Hint:** "Asserts no exception" with no value check is usually shallow.
- **Key Takeaway:** AI generates tests fast, but many give false confidence. Every test must answer: "What real behavior does this protect?"

---

## Validation / Success Criteria

You are done when:

- [ ] `pytest -v` is green with happy-path, negative, and edge tests for `parse_task`.
- [ ] A fixture backs at least one test.
- [ ] A parametrized test covers `priority_score` boundaries.
- [ ] A coverage report runs and you can explain a `Missing` line.
- [ ] The starter's failing test is green via a **code** fix (🧩 Debug/Fix).
- [ ] You critiqued and improved one AI-generated test (Exercise C).

**Definition of Done:** Commit `tests/test_taskutils.py` on `feature/taskutils-tests` and open a merge request. Note your coverage percentage and one meaningful test you're proud of.

## Troubleshooting

- **Symptom:** `pytest` finds no tests.
  **Likely cause:** File or function not named `test_*`.
  **Fix:** Use `tests/test_taskutils.py` and functions starting with `test_`.

- **Symptom:** `ModuleNotFoundError: app`.
  **Likely cause:** Running from the wrong directory.
  **Fix:** Run `pytest` from the project root; ensure `app/__init__.py` and `tests/__init__.py` exist.

- **Symptom:** `pytest.raises` test fails with "DID NOT RAISE".
  **Likely cause:** The function isn't actually raising for that input.
  **Fix:** Confirm the input really is invalid; check your `parse_task` validation.

- **Symptom:** Coverage command errors with "unrecognized arguments".
  **Likely cause:** `pytest-cov` not installed.
  **Fix:** `pip install pytest-cov`.

## Stretch Goal / Extension

Add a `conftest.py` in `tests/` and move `sample_tasks` there so every test file can share it. Confirm tests still pass with the fixture defined once, globally.

## Using Claude Code in This Lab

Ask Claude Code to brainstorm edge cases, then judge them:
> *"Suggest edge and boundary test cases for `parse_task` that I might be missing. List the cases and why each matters — don't write the full tests yet."*

**Required manual verification:** For each suggested case, write the test yourself and confirm it protects real behavior. Delete any that just assert "no crash."

**No-AI fallback:** Brainstorm with the four-category checklist (happy/negative/edge/boundary) by hand.

## Key Takeaways

- A single function needs several tests; verifying *rejection* of bad input is not optional.
- AAA and clear names make a failing test read like a sentence.
- Fixtures reuse setup; parametrization makes edge cases cheap to add.
- Coverage guides you but never proves correctness — meaningful assertions do.
- A failing test is information; fix the code, never weaken the test.
- AI-generated tests need human review; a shallow test is worse than none.
