# Module 1.6 Lab — Teach the Engine to Decide

## Overview

Your triage engine can clean a title — but a clean title is just *display*. In this lab the same `app/task_triage.py` grows two superpowers. First, **decisions**: you'll turn plain-English business rules ("critical scores higher than low," "anything marked urgent jumps to high") into code with conditionals and Boolean logic. Second, **collections**: you'll scale from one task to a whole **list of dictionaries** — the JSON-like records real APIs and databases pass around all day — and loop over them to print a per-task report.

Nothing gets thrown away. The title cleaner from Module 1.5 stays; you're stacking new features on top.

## Learning Objectives

By the end of this lab you will be able to:

- Write `if`/`elif`/`else` logic using comparison operators (`==`, `!=`, `>`, `<`).
- Combine conditions with Boolean logic (`and`, `or`, `not`) and membership (`in`).
- Convert business rules into code: a priority → score table and an auto-escalate rule.
- Build and loop lists with `for` and `enumerate()`.
- Model a task as a **dictionary** and read fields safely with `[ ]` vs `.get()`.
- Loop over a **list of dictionaries** to print a clean per-task report line.

## Prerequisites

- **Module 1.5 complete:** a running `app/task_triage.py` that cleans titles and builds slugs.
- Comfort with the edit → run → read → fix loop and f-strings.
- Companion reading: [modules/module-01.6/student-handout.md](../modules/module-01.6/student-handout.md).

## Estimated Time

~60 minutes (core path). The short challenge exercises add ~35 minutes.

## Environment and Setup

```bash
cd taskflow
source .venv/bin/activate          # prompt shows (.venv)
git checkout -b feature/triage-decisions
```

You'll keep editing **`app/task_triage.py`** from Module 1.5 — do **not** start a new file.

Companion code files (reference implementations, generated separately):

- [code/module-01.6-starter.py](../code/module-01.6-starter.py) — `TODO`s for scoring/urgent logic and a list-of-dicts loop, **plus one intentional `KeyError` bug** on a missing field.
- [code/module-01.6-example.py](../code/module-01.6-example.py) — a runnable reference for this module's portion.

## Scenario

The TaskFlow team needs the engine to *make decisions*: Which tasks are urgent? Which are high priority? Which still need work? And it must do this for *many* tasks at once. Worse, real incoming data is incomplete — one task arrives with **no owner field at all**. Your engine must score, escalate, and report without crashing on that missing data.

## Tasks

### Task 1: Score a priority

#### Goal
Turn the priority → score table into an `if`/`elif`/`else` chain.

#### 🔍 Think First (do not skip)
The team's rule:

| Priority | Score |
|---|---:|
| critical | 4 |
| high | 3 |
| medium | 2 |
| low | 1 |
| missing / unknown | 0 |

Before coding, answer:

- What should happen if the priority is `"banana"` or an empty string? (Hint: it must **not** crash.)
- Which part of an `if`/`elif`/`else` chain is your "catch everything else" safety net?

#### Steps
1. In `app/task_triage.py`, add:
   ```python
   priority = "high"

   if priority == "critical":
       score = 4
   elif priority == "high":
       score = 3
   elif priority == "medium":
       score = 2
   elif priority == "low":
       score = 1
   else:
       score = 0   # missing or unknown — never crash

   print(f"{priority} → {score}")
   ```
2. Run it, then change `priority` to `"banana"` and run again.

#### Checkpoint
Every priority maps to the right number, and an unknown value yields `0` instead of crashing.

#### Expected Output
```text
high → 3
```
(After changing to `"banana"`: `banana → 0`.)

> **💡 Why this matters:** Real data has typos and blanks. The `else` branch is your safety net — backend rules become behavior through conditionals, and the catch-all keeps messy input from crashing the whole engine.

> **🤔 Reflect:** You just built a tiny **rules engine** — a table of business rules turned into code. The same pattern (map a category to a number, then act on it) runs fraud scoring, loan approvals, and ticket routing at real companies. What you changed here is small; the idea scales to millions of decisions a day.

---

### Task 2: Auto-escalate urgent tasks

#### Goal
Use `in` and Boolean logic to bump any "urgent" task to high priority, then decide if it needs attention.

#### 🔍 Think First (do not skip)
- The `in` operator checks membership: `"urgent" in "urgent: deploy"` is `True`. Why lowercase the title *before* checking?
- "Needs attention" means **not done** AND priority is **high or critical**. How do you combine those with `and`, `or`, and `not`?

#### Steps
1. Add:
   ```python
   title = "URGENT: deploy hotfix"
   priority = "medium"
   done = False

   if "urgent" in title.lower():
       priority = "high"          # auto-escalate

   if (priority == "critical" or priority == "high") and not done:
       print("This task needs immediate attention.")
   ```
2. Run it. Then set `done = True` and run again — the message should **not** print.

#### Checkpoint
An urgent, not-done task prints the attention message; a done task prints nothing.

#### Expected Output
```text
This task needs immediate attention.
```

> **🏭 In production:** That `"urgent" in title` check is exactly how real systems do keyword routing — flagging support tickets, filtering spam, tagging logs. Same idea, bigger scale.

---

### Task 3: Model tasks as a list of dictionaries

#### Goal
Store tasks as **dictionaries** in a **list** — the real shape of backend data.

#### 🔍 Think First (do not skip)
A plain string can't hold everything about a task. A **dictionary** stores `key → value` pairs, so one task carries its title, priority, status, and owner together. Look at the data below — **one task is missing its `owner` key entirely.** What do you predict happens if you read `task["owner"]` on that one?

#### Steps
1. Add the task list (paste exactly — the missing `owner` is intentional):
   ```python
   tasks = [
       {"title": "  fix LOGIN bug  ", "priority": "critical", "done": False, "owner": "engineering"},
       {"title": "Update onboarding docs", "priority": "medium", "done": False, "owner": "documentation"},
       {"title": "review pull request", "priority": "high", "done": True, "owner": "engineering"},
       {"title": "deploy hotfix", "priority": "high", "done": False},   # no owner!
   ]

   print(f"Loaded {len(tasks)} tasks.")
   print(tasks[0]["title"])          # read the first task's title
   ```
2. Run it.

#### Checkpoint
The script reports the task count and prints the first task's raw title.

#### Expected Output
```text
Loaded 4 tasks.
  fix LOGIN bug  
```

> **💡 Why this matters:** This `{ }` shape *is* JSON. It's what APIs send and receive and what database rows become in Python. Get comfortable here and Module 06 will feel like home.

---

### Task 4: Print a numbered per-task report

#### Goal
Loop the list with `enumerate()` and print one clean report line per task — surviving the missing owner.

#### Steps
1. Add the report loop:
   ```python
   print("\nAll Tasks:")
   for number, task in enumerate(tasks, start=1):
       title = task["title"].strip().title()
       owner = task.get("owner", "unassigned")
       status = "done" if task["done"] else "open"
       print(f"{number}. {title} | {task['priority']} | {owner} | {status}")
   ```
2. Run it.

#### Checkpoint
All four tasks print, numbered from 1, and the owner-less task shows `unassigned` — **no `KeyError`**.

#### Expected Output
```text
All Tasks:
1. Fix Login Bug | critical | engineering | open
2. Update Onboarding Docs | medium | documentation | open
3. Review Pull Request | high | engineering | done
4. Deploy Hotfix | high | unassigned | open
```

> **🧠 Remember:** `task["owner"]` *demands* the key and crashes if it's missing. `task.get("owner", "unassigned")` *requests* it and falls back gracefully. At any boundary where data might be incomplete — which is always — reach for `.get()`. And note `enumerate(tasks, start=1)` numbers from 1, not 0.

---

## 🧠 Your Turn — Count the open tasks

The report shows each task's status; now produce a *summary number*.

- **Goal:** Loop the `tasks` list and count how many are **not done**. Print `Open tasks: N`.
- **Constraints:** Use a counter variable that starts at `0` and a `for` loop; read `done` from each task.
- **Expected outcome:** `Open tasks: 3` (only "Review Pull Request" is done).

**Hint:** Start `open_count = 0`, then inside the loop, `if not task["done"]: open_count += 1`.

Design it yourself — no full solution is provided here. (The instructor solution has a model answer.)

---

## 🧩 Debug / Fix — The missing-field `KeyError`

Open [code/module-01.6-starter.py](../code/module-01.6-starter.py) and run it:

```bash
python code/module-01.6-starter.py
```

It **crashes** partway through the report. The buggy line looks like:

```python
print(f"{number}. {title} | {task['priority']} | {task['owner']} | {status}")
#                                                  ^^^^^^^^^^^^^ crashes on the owner-less task
```

- **Symptom:** The first few tasks print, then the script dies with `KeyError: 'owner'`.
- **Likely cause:** `task["owner"]` uses **bracket access**, which *demands* the key. The "deploy hotfix" task has no `owner`, so Python raises `KeyError` and stops everything.
- **Your task:** Replace the bracket access with `task.get("owner", "unassigned")` so the missing field falls back gracefully. Re-run and confirm all four tasks print.

**Success criteria:** All four tasks print; the owner-less task shows `unassigned`; no traceback.

**Hint:** `.get("owner", "unassigned")` *requests* the key and supplies a fallback instead of crashing.

> **🤔 Reflect — what would break in a real system?** Picture this loop inside an API that returns tasks as JSON. With bracket access, *one* record missing an `owner` doesn't just skip that row — it throws a `KeyError` that becomes a `500 Internal Server Error`, and the user sees *nothing*. With `.get()`, the response goes out clean and that one task just reads `unassigned`. Same data, same bug, wildly different blast radius. That's why this one-character habit matters.

> **🧠 Remember:** Bracket access (`task["owner"]`) is for keys you *know* exist. The moment data might be incomplete — which is at every real boundary — use `.get("key", default)`. This single habit prevents a whole category of production crashes.

---

## Short Challenge Exercises

### Exercise A — Score every task in the list

- **Estimated Time:** 12 min
- **Goal:** Reuse your scoring logic across the whole list.
- **Starter Context:** Your `tasks` list and the priority → score chain from Task 1.
- **Task Instructions:**
  1. Loop the `tasks` list.
  2. For each task, compute its score from `task["priority"]` (reuse your `if/elif/else`).
  3. Print `f"{title} → {score}"` per task.
- **Success Criteria:** Each task prints with the correct numeric score; the `done` "Review Pull Request" still scores `3` (scoring ignores status).
- **Expected Result:** `Fix Login Bug → 4`, `Deploy Hotfix → 3`, etc.
- **Optional Hint:** You can copy the chain inside the loop for now — Module 1.7 turns it into a reusable function.
- **Key Takeaway:** Business rules applied across a list are the core of triage; soon you'll stop copy-pasting the logic and make it a function.

### Exercise B — Count tasks needing attention

- **Estimated Time:** 12 min
- **Goal:** Combine Boolean logic with a loop counter.
- **Starter Context:** The "needs attention" rule from Task 2 (not done AND high/critical).
- **Task Instructions:**
  1. Start `attention_count = 0`.
  2. Loop `tasks`; for each, check `not task["done"] and task["priority"] in ("high", "critical")`.
  3. Increment the counter on a match and print `Needs attention: N` at the end.
- **Success Criteria:** The count is `2` (Fix Login Bug + Deploy Hotfix).
- **Expected Result:** `Needs attention: 2`.
- **Optional Hint:** `task["priority"] in ("high", "critical")` checks membership against two allowed values at once.
- **Key Takeaway:** Counting matches while looping is how backends produce summary metrics — and this exact count powers your final report in Module 1.7.

### Exercise C — 🧪 Experiment: bracket vs `.get()`

- **Estimated Time:** 10 min
- **Goal:** Feel the difference between the two ways to read a dict field.
- **Starter Context:** The owner-less "deploy hotfix" task.
- **Task Instructions:**
  1. On the owner-less task, try `print(task["owner"])` and run. Observe the crash.
  2. Change it to `print(task.get("owner"))` and run. What prints now?
  3. Change it to `print(task.get("owner", "unassigned"))`. What changed?
- **Success Criteria:** You can describe what each of the three lines does (crash / `None` / fallback text).
- **Expected Result:** Crash → `None` → `unassigned`.
- **Optional Hint:** `.get()` with no default returns `None`; with a default it returns your fallback.
- **Key Takeaway:** `[ ]` demands, `.get()` requests; the default turns a missing field from a crash into a sensible value.

---

## Validation / Success Criteria

You are done when:

- [ ] An `if/elif/else` chain scores every priority, including unknown → `0` (Task 1).
- [ ] Urgent titles auto-escalate to high, and the attention check works (Task 2).
- [ ] `tasks` is a list of dictionaries, one of which is missing `owner` (Task 3).
- [ ] A numbered per-task report prints all four tasks, owner-less one shows `unassigned` (Task 4).
- [ ] You counted the open tasks correctly (🧠 Your Turn).
- [ ] The starter's `KeyError` is fixed with `.get()` (🧩 Debug/Fix).

**Definition of Done:** Commit `app/task_triage.py` on the `feature/triage-decisions` branch and (optionally) open a merge request.

```bash
git add app/task_triage.py
git commit -m "Add scoring, urgent escalation, and per-task report"
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `KeyError: 'owner'` mid-report | Bracket access on the missing field | Use `task.get("owner", "unassigned")` |
| `SyntaxError` on an `if` line | Used `=` (assign) instead of `==` (compare) | `if priority == "high":` — double equals to compare |
| Report numbers start at `0` | `enumerate(tasks)` without `start=1` | `enumerate(tasks, start=1)` |
| Unknown priority crashes | No `else` branch in the chain | Add `else: score = 0` to catch everything |
| Attention check never matches | Compared against `"High"` (wrong case) | Data is `"high"` — normalize/compare lowercase |
| `done` shows `True`/`False` not `done`/`open` | Printed the raw Boolean | Use `"done" if task["done"] else "open"` |

## Stretch Goal / Extension

Add a fifth task to your list that contains the word **"urgent"** in its title but has `priority: "low"`. Then add the auto-escalate check from Task 2 *inside* your report loop, so any urgent task is bumped to `high` **before** its line prints. Confirm your new task shows `high` in the report even though its raw data said `low`. This previews how Module 1.7 composes rules into the final report.

## Using Claude Code in This Lab

Use Claude Code to **explain and trace**, not to write your logic:

> *"Explain why `task['owner']` crashes but `task.get('owner', 'unassigned')` doesn't, with a tiny example."*

> *"For `(priority == 'critical' or priority == 'high') and not done`, list the input combinations where this is True."*

**Required manual verification:** Run your report loop against the owner-less task yourself and confirm it prints `unassigned` instead of crashing.

**No-AI fallback:** Print the value just before the line that breaks (`print(task)`), then check which key is missing. The skill is reasoning about what the data actually contains — AI just speeds it up.

## Key Takeaways

- Conditionals turn plain-English business rules into program behavior; the `else` branch is your safety net.
- Combine conditions with `and`, `or`, `not`, and membership with `in`.
- Lists hold many ordered items; loop them with `for` and number them with `enumerate(..., start=1)`.
- Dictionaries model real records as key → value pairs — the shape of JSON and DB rows.
- `task["key"]` crashes on missing data; `task.get("key", default)` stays safe.
- Counting matches while looping is how summary metrics get built.

**Next:** In **Module 1.7**, you'll fold this growing-but-repetitive script into clean, reusable **functions** and assemble the full **TaskFlow Triage Report** — the finished artifact.
