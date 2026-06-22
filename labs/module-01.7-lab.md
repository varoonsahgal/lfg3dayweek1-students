# Module 1.7 Lab — Functions & the TaskFlow Triage Report

## Overview

Your triage engine *works* — but look at it. The title-cleaning logic is copy-pasted in several places. The scoring `if/elif` chain shows up wherever you need a number. Every tweak means changing the same thing in five spots and missing one.

This lab is the cure. You'll learn **functions** — named, reusable chunks of logic — and fold all that duplication into a handful of clean tools: `clean_title`, `priority_to_score`, `is_attention_needed`, and `print_task_report`. Then you'll add two **filter helpers** (`tasks_needing_attention`, `tasks_for_owner`) and snap everything together into the finished **TaskFlow Triage Report**.

This is the capstone of the Python Crash Lab. When you're done, `app/task_triage.py` looks like the start of real application code — the perfect on-ramp to Module 02.

## Learning Objectives

By the end of this lab you will be able to:

- Write functions with `def`, parameters, arguments, and `return` values.
- Explain the difference between **printing** and **returning** — and choose correctly.
- Extract repeated logic into small, single-responsibility functions.
- Write filter functions that return a subset of tasks.
- Compose functions to assemble the complete TaskFlow Triage Report.

## Prerequisites

- **Module 1.5 + 1.6 complete:** a working `app/task_triage.py` that cleans titles, scores priorities, and loops over a list of task dicts.
- Comfort with the edit → run → read → fix loop, f-strings, conditionals, and dicts.
- Companion reading: [modules/module-01.7/student-handout.md](../modules/module-01.7/student-handout.md).

## Estimated Time

~60 minutes (core path). The short challenge exercises add ~40 minutes.

## Environment and Setup

```bash
cd taskflow
source .venv/bin/activate          # prompt shows (.venv)
git checkout -b feature/triage-report
```

You'll keep editing **`app/task_triage.py`** — the same file you've grown since Module 1.5. Do **not** start over.

Companion code files (reference implementations, generated separately):

- [code/module-01.7-starter.py](../code/module-01.7-starter.py) — function stubs with `TODO`s, **including one intentional print-vs-return bug**.
- [code/module-01.7-example.py](../code/module-01.7-example.py) — the **complete reference** `task_triage.py` that prints the full report.

## Scenario

The triage logic is correct but tangled — duplicated cleanup, repeated scoring chains, a report assembled by hand. The TaskFlow team wants a single, clean report they can run any time: every task listed, a summary of counts, and a focused "needs attention" list. Your job is to refactor the tangle into functions, then compose them into that finished report.

The data your report runs on (carry it forward from Module 1.6):

```python
tasks = [
    {"title": "  fix LOGIN bug  ", "priority": "critical", "done": False, "owner": "engineering"},
    {"title": "Update onboarding docs", "priority": "medium", "done": False, "owner": "documentation"},
    {"title": "review pull request", "priority": "high", "done": True, "owner": "engineering"},
    {"title": "deploy hotfix", "priority": "high", "done": False},   # no owner!
]
```

## Tasks

### Task 1: Extract `clean_title` and `priority_to_score`

#### Goal
Turn copy-pasted cleanup and scoring into two reusable functions that **return** values.

#### 🔍 Think First (do not skip)
- A **parameter** is the name in the `def` (`raw`); an **argument** is the real value you pass in (`"  fix LOGIN bug  "`). Why does the function need to `return` the cleaned title instead of `print()`-ing it?
- Your scoring chain currently lives inline. If you wrap it in a function that `return`s the score, what can you now *do* with that number that you couldn't before?

#### Steps
1. At the **top** of `app/task_triage.py` (above your task data), define:
   ```python
   def clean_title(raw):
       """Return a display-ready title."""
       return raw.strip().title()


   def priority_to_score(priority):
       """Return a numeric weight for a priority (unknown -> 0)."""
       if priority == "critical":
           return 4
       elif priority == "high":
           return 3
       elif priority == "medium":
           return 2
       elif priority == "low":
           return 1
       return 0
   ```
2. Quick-check them:
   ```python
   print(clean_title("  fix LOGIN bug  "))   # Fix Login Bug
   print(priority_to_score("high"))           # 3
   ```

#### Checkpoint
Both functions return (not print) the right value, and you can store the result in a variable.

#### Expected Output
```text
Fix Login Bug
3
```

> **💡 Why this matters:** A function is "write once, call everywhere." When the cleanup rule changes, you edit *one* place. And because `priority_to_score` **returns**, you can add scores, compare them, and feed them into the report — that's reuse.

---

### Task 2: Write `is_attention_needed` (a function that returns a Boolean)

#### Goal
Capture the "needs attention" rule in one function that returns `True`/`False`.

#### 🔍 Think First (do not skip)
A task needs attention when it is **NOT done** AND its priority is **high or critical**. Why return a Boolean instead of printing a message? (Hint: you're about to *count* how many tasks need attention — you can't count printed text.)

#### Steps
1. Add:
   ```python
   def is_attention_needed(task):
       """True when a task is NOT done AND high/critical priority."""
       not_done = not task["done"]
       urgent_priority = task["priority"] in ("high", "critical")
       return not_done and urgent_priority
   ```
2. Test it on two tasks:
   ```python
   print(is_attention_needed(tasks[0]))   # True  (critical, open)
   print(is_attention_needed(tasks[2]))   # False (high, but done)
   ```

#### Checkpoint
The function returns `True` for an open high/critical task and `False` for a done one.

#### Expected Output
```text
True
False
```

> **🏭 In production:** Small, single-purpose functions make a codebase changeable. When the "needs attention" rule changes, you edit *one* function and every part of the app that uses it updates at once.

> **🤔 Reflect:** Notice how easy `is_attention_needed` is to *check*: hand it a task, look at the answer, done. That's not luck — a function with clear inputs and one returned output is exactly what makes code **testable**. In Module 03 you'll write automated tests for functions shaped just like this one. A function that printed instead of returned would be far harder to pin down — you can't easily assert on something that only flashed on the screen.

---

### Task 3: Write the filter helpers

#### Goal
Build `tasks_needing_attention(tasks)` and `tasks_for_owner(tasks, owner)` — functions that **return new lists**.

#### Steps
1. Add (use either a comprehension or a plain loop — both shown):
   ```python
   def tasks_needing_attention(tasks):
       """Return only the tasks that need attention."""
       return [t for t in tasks if is_attention_needed(t)]


   def tasks_for_owner(tasks, owner):
       """Return only the tasks belonging to a given owner."""
       result = []
       for t in tasks:
           if t.get("owner") == owner:
               result.append(t)
       return result
   ```
2. Test:
   ```python
   print(len(tasks_needing_attention(tasks)))      # 2
   print(len(tasks_for_owner(tasks, "engineering")))  # 2
   ```

#### Checkpoint
Each filter returns a **new** list; the original `tasks` is unchanged.

#### Expected Output
```text
2
2
```

> **🧠 Remember:** Filters return *new lists*. The original `tasks` is untouched, so you can filter it many different ways without breaking anything. Note `tasks_for_owner` uses `.get("owner")` so the owner-less task doesn't crash it.

---

### Task 4: Assemble the full TaskFlow Triage Report

#### Goal
Compose your functions into `print_task_report` plus a summary section — the finished artifact.

#### 🔍 Think First (do not skip)
Every count in the summary (total, completed, open, needs-attention) is built by *adding up returned values* from your functions and the list. If `is_attention_needed` *printed* instead of *returned*, could you build the `Needs attention:` count? Why not?

#### Steps
1. Add the report function:
   ```python
   def print_task_report(tasks):
       """Print the per-task section of the report."""
       print("All Tasks:")
       for number, task in enumerate(tasks, start=1):
           title = clean_title(task["title"])
           owner = task.get("owner", "unassigned")
           status = "done" if task["done"] else "open"
           print(f"{number}. {title} | {task['priority']} | {owner} | {status}")
   ```
2. At the **bottom** of the file, assemble the whole report:
   ```python
   print("TASKFLOW TRIAGE REPORT")
   print("======================")
   print()

   print_task_report(tasks)
   print()

   total = len(tasks)
   completed = len([t for t in tasks if t["done"]])
   open_count = total - completed
   attention = tasks_needing_attention(tasks)

   print("Summary:")
   print(f"Total tasks: {total}")
   print(f"Completed: {completed}")
   print(f"Open: {open_count}")
   print(f"Needs attention: {len(attention)}")
   print()

   print("Tasks Needing Attention:")
   for task in attention:
       print(f"- {clean_title(task['title'])}")
   ```
3. Run the full file:
   ```bash
   python app/task_triage.py
   ```

#### Checkpoint
The script prints the complete, correctly-formatted report — counts and the needs-attention list agree with each other.

#### Expected Output
```text
TASKFLOW TRIAGE REPORT
======================

All Tasks:
1. Fix Login Bug | critical | engineering | open
2. Update Onboarding Docs | medium | documentation | open
3. Review Pull Request | high | engineering | done
4. Deploy Hotfix | high | unassigned | open

Summary:
Total tasks: 4
Completed: 1
Open: 3
Needs attention: 2

Tasks Needing Attention:
- Fix Login Bug
- Deploy Hotfix
```

> **💡 Why this matters:** Because every helper **returns**, the report is just gluing returned values together with f-strings. The `Needs attention: 2` count and the two listed titles come from the *same* `tasks_needing_attention(tasks)` call — so they can never disagree. That's the power of composing returning functions.

> **🤔 Reflect:** Step back and look at what you built: pull a list of records, score them, *filter to the ones that need a human right now*, show counts at the top. That's the skeleton of every on-call dashboard and triage tool in the industry. Swap `tasks` for alerts, support tickets, or failing health-checks and you have a real monitoring page. You didn't build a toy — you built the *shape* teams stare at all day.

---

## 🧠 Your Turn — Add a "Completed Tasks" section

The report shows open work prominently; now surface the *done* work too.

- **Goal:** After the needs-attention list, print a `Completed Tasks:` section listing the title of every task where `done` is `True`.
- **Constraints:** Reuse `clean_title`; build the completed list with a comprehension or a loop; don't modify the existing sections.
- **Expected outcome:**
  ```text
  Completed Tasks:
  - Review Pull Request
  ```

**Hint:** `completed_tasks = [t for t in tasks if t["done"]]`, then loop and print `- {clean_title(t['title'])}`.

Design it yourself — no full solution is provided here. (The instructor solution has a model answer.)

---

## 🧩 Debug / Fix — The print-vs-return bug

Open [code/module-01.7-starter.py](../code/module-01.7-starter.py) and run it:

```bash
python code/module-01.7-starter.py
```

The summary counts come out **wrong** (e.g. `Needs attention: 0`, or a `TypeError` about `None`). The culprit is a helper that **prints instead of returns**:

```python
def is_attention_needed(task):
    not_done = not task["done"]
    urgent_priority = task["priority"] in ("high", "critical")
    print(not_done and urgent_priority)     # ❌ prints the answer, returns None
```

- **Symptom:** `tasks_needing_attention` (which calls `is_attention_needed`) keeps *no* tasks, so the count is `0` — even though `True`/`False` values flash on the screen. Or the report crashes trying to use a `None` result.
- **Likely cause:** The function `print()`s its result and never `return`s it. A function with no `return` hands back `None`, so every caller sees `None` (which is falsy) instead of the real Boolean.
- **Your task:** Change `print(...)` to `return ...`, then re-run. The counts and the needs-attention list should snap into place.

**Success criteria:** After the fix, `Needs attention: 2` and the list shows `Fix Login Bug` and `Deploy Hotfix`.

**Hint:** A function whose result you *store* but that uses `print()` will leave your variable as `None`. If the report needs the value, **return** it.

> **🧠 Remember:** **Print is for showing a human. Return is for feeding the rest of your program.** A function that prints can put text on the screen, but it can't hand its result to your report. Composition requires returning.

---

## Short Challenge Exercises

### Exercise A — Highest-priority task finder

- **Estimated Time:** 15 min
- **Goal:** Write a function that returns the single most urgent task.
- **Starter Context:** Your `priority_to_score` function and the `tasks` list.
- **Task Instructions:**
  1. Write `highest_priority_task(tasks)` that loops the list and **returns** the task with the largest `priority_to_score`.
  2. Print its cleaned title.
  3. Confirm it picks `Fix Login Bug` (critical = 4).
- **Success Criteria:** The function returns one task dict; its title is `Fix Login Bug`.
- **Expected Result:** `Most urgent: Fix Login Bug`.
- **Optional Hint:** Track a `best` task and a `best_score`; update both when you find a higher score.
- **Key Takeaway:** A function that returns the "winner" of a loop is a reusable building block — and it leans on `priority_to_score` instead of re-implementing it.

### Exercise B — Group tasks by owner

- **Estimated Time:** 15 min
- **Goal:** Reuse `tasks_for_owner` to print a per-owner breakdown.
- **Starter Context:** Your `tasks_for_owner(tasks, owner)` filter.
- **Task Instructions:**
  1. For each owner in `["engineering", "documentation", "unassigned"]`, call `tasks_for_owner`.
  2. Print the owner, then each of their task titles indented below.
  3. Make sure the owner-less task shows up under `unassigned`.
- **Success Criteria:** Every task appears under exactly one owner; `Deploy Hotfix` lands under `unassigned`.
- **Expected Result:**
  ```text
  engineering:
    - Fix Login Bug
    - Review Pull Request
  documentation:
    - Update Onboarding Docs
  unassigned:
    - Deploy Hotfix
  ```
- **Optional Hint:** `tasks_for_owner` compares `t.get("owner")` to the owner — but the owner-less task's `.get("owner")` is `None`, not `"unassigned"`. Decide how to handle that (see the solution).
- **Key Takeaway:** Reusing a filter for many inputs is composition in action — and edge cases like a `None` owner are exactly what real code must handle.

### Exercise C — Slugs for all tasks

- **Estimated Time:** 12 min
- **Goal:** Add a function that returns a slug, reusing Module 1.5's logic.
- **Starter Context:** Your `clean_title` function.
- **Task Instructions:**
  1. Write `title_to_slug(title)` that **returns** a slug (lowercase, dashes for spaces).
  2. Loop the tasks and print `title → slug` for each.
  3. Confirm `Fix Login Bug → fix-login-bug`.
- **Success Criteria:** Each task prints a correct slug; the function returns (not prints) the slug.
- **Expected Result:** `Fix Login Bug → fix-login-bug`.
- **Optional Hint:** `clean_title(raw).lower().replace(" ", "-")`.
- **Key Takeaway:** Composing `title_to_slug` on top of `clean_title` shows how small returning functions stack into bigger features.

---

## Validation / Success Criteria

You are done when:

- [ ] `clean_title` and `priority_to_score` are functions that **return** values (Task 1).
- [ ] `is_attention_needed` returns a Boolean (Task 2).
- [ ] `tasks_needing_attention` and `tasks_for_owner` return new lists (Task 3).
- [ ] Running `app/task_triage.py` prints the **full** report matching the expected output exactly (Task 4).
- [ ] A `Completed Tasks:` section was added (🧠 Your Turn).
- [ ] The starter's print-vs-return bug is fixed; counts are correct (🧩 Debug/Fix).

**Definition of Done:** Commit the finished `app/task_triage.py` on `feature/triage-report` and open a merge request. In the description, note that the script is "refactored into reusable functions, ready for Module 02."

```bash
git add app/task_triage.py
git commit -m "Refactor into functions and assemble the full triage report"
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Needs attention: 0` but Trues print to screen | A helper `print()`s instead of `return`s | Change `print(...)` to `return ...` (the Debug/Fix) |
| A stored result is `None` | The function has no `return` | Add `return`; a function without it hands back `None` |
| `TypeError: object of type 'NoneType' has no len()` | Filtering on a printing helper that returns `None` | Fix the helper to return its Boolean |
| Report counts disagree with the listed titles | You computed the count and the list separately | Compute the list once (`attention = ...`) and use `len(attention)` |
| `KeyError: 'owner'` in `print_task_report` | Bracket access on the missing field | Use `task.get("owner", "unassigned")` |
| Title shows raw (`  fix LOGIN bug  `) | Forgot to call `clean_title` | Wrap the title in `clean_title(...)` |

## Stretch Goal / Extension

Add a tiny **CLI menu** at the bottom of the file: use `input("Choose: [a]ll, [n]eeds attention, [q]uit > ")` in a `while True:` loop. On `a`, call `print_task_report(tasks)`; on `n`, print the needs-attention list; on `q`, break. This turns your report into an interactive tool — and previews the request → response loop you'll build for real in later modules. *(Keep it simple: no error handling required beyond an `else` for unknown choices.)*

For an extra challenge, add a `validate_task(task)` function that returns `True` only if a task has a non-empty `title` and a known `priority`, and use it to skip malformed tasks before reporting.

## Using Claude Code in This Lab

Use Claude Code to **spot bugs and suggest refactors** — then verify every change yourself:

> *"My function stores a value but it's `None`. Here's the code — is this a print-vs-return bug? [paste function]."*

> *"Suggest how to break this long report function into smaller single-responsibility functions, but keep the output identical."*

**Required manual verification:** Run the script and compare against the expected TASKFLOW TRIAGE REPORT **line by line**. If a refactor changes the output, revert and investigate before accepting.

**No-AI fallback:** Add `print(repr(value))` right after a function call to see what actually came back. If it's `None`, you have a print-vs-return bug. The skill is reasoning about inputs and outputs — AI just speeds it up.

## Key Takeaways

- Functions (`def`, parameters, arguments, `return`) are the core unit of backend code.
- **Return** values when your program needs them; **print** only for humans at the end.
- A function that prints can't feed the report — composition requires returning.
- Extract repeated logic into small, single-responsibility functions.
- Filters return reusable subsets so counts and lists stay in sync.
- Composing returning functions is how the full triage report is assembled.

**Next:** In **Module 02 — Python Fundamentals**, you'll take these very functions further with comprehensions, custom exceptions, importable modules, and your first classes — turning `task_triage.py` into testable, production-style code.
