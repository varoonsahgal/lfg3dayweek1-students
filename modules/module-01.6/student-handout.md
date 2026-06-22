# Module 1.6 — Python Crash Lab: Task Decisions & Collections

## Overview

Your triage engine can clean a title — but a clean title is just *display*. The TaskFlow team needs the engine to **make decisions**: Which tasks are urgent? Which are high priority? Which still need work? And it has to do this for *many* tasks at once, not one hardcoded example.

In this module the same `app/task_triage.py` grows two superpowers. First, **decisions**: you'll turn plain-English business rules ("critical tasks score higher than low ones," "anything marked urgent jumps to high priority") into code using conditionals and Boolean logic. Second, **collections**: you'll scale from one task to a whole list, then upgrade each task into a **dictionary** — the JSON-like record that real APIs and databases pass around all day.

Nothing gets thrown away. The title cleaner from Module 1.5 stays; you're stacking new features on top.

## Why This Matters

Backend code is mostly two things: **deciding** and **looping**. An API decides whether a request is allowed. A billing job loops over thousands of invoices deciding which are overdue. A search endpoint loops over records deciding which match. The `if/elif/else` and `for` you learn here are the literal building blocks of that work.

And the **list of dictionaries** you build by the end of this module? That's not a toy. It's the exact shape of data you'll get back from a database query or a JSON API in Module 06. Learn to loop over it and pull fields out safely now, and that future work will feel familiar instead of foreign.

## Learning Objectives

By the end of this module, you can:

- Write `if`/`elif`/`else` logic using comparison operators (`==`, `!=`, `>`, `<`).
- Combine conditions with Boolean logic (`and`, `or`, `not`) and membership (`in`).
- Convert business rules into code: a priority → score table and an auto-escalate rule.
- Build and grow lists: indexing, `append()`, `len()`, counting, `for`, and `enumerate()`.
- Model a task as a **dictionary** and read fields with `[ ]` vs `.get()`.
- Loop over a **list of dictionaries** to print a clean per-task report line.

## Prerequisites

- **Module 1.5:** a running `app/task_triage.py` that cleans titles and builds slugs.
- Comfort with the edit → run → read → fix loop and f-strings.
- **Next:** this module leads directly into **Module 1.7 — Functions & the Triage Report**.

## Key Concepts

### 1. Conditionals: turning rules into behavior

A **conditional** runs different code depending on whether something is true. `if` checks a condition; `elif` ("else if") checks another; `else` is the fallback:

```python
priority = "critical"

if priority == "critical":
    print("Drop everything.")
elif priority == "high":
    print("Do it today.")
else:
    print("Schedule it.")
```

> **💡 Why this matters:** Notice this reads like an English policy. That's the whole point — backend rules ("if the user is unverified, block the action") are conditionals. You're translating business requirements into behavior.

### 2. Comparison operators and truthy/falsy

Conditions are questions that answer `True` or `False`:

| Operator | Asks | Example |
|---|---|---|
| `==` | equal? | `priority == "high"` |
| `!=` | not equal? | `done != True` |
| `>` `<` | greater / less | `score > 2` |

Python also treats some values as "empty" (**falsy**) and others as "has something" (**truthy**). Empty string `""`, the number `0`, and `None` are falsy; most everything else is truthy:

```python
title = ""
if not title:          # empty string is falsy
    print("Title is missing!")
```

> **🧠 Remember:** A single `=` *assigns* a value; a double `==` *compares*. Mixing them up is the #1 beginner conditional bug.

### 3. Boolean logic: `and`, `or`, `not`, `in`

Real rules combine conditions. Use `and` (both must be true), `or` (either), `not` (flip it), and `in` (is it inside?):

```python
priority = "critical"
done = False

if (priority == "critical" or priority == "high") and not done:
    print("This task needs immediate attention.")
```

The `in` operator checks membership — perfect for spotting keywords:

```python
title = "urgent: deploy hotfix"
if "urgent" in title.lower():
    print("Auto-escalating to high priority.")
```

> **🏭 In production:** That `"urgent" in title` check is exactly how real systems do keyword routing — flagging support tickets, filtering spam, tagging logs. Same idea, bigger scale.

### 4. The priority → score table

The team's rule: each priority is worth a number, so the engine can sort and compare. Turn the table into code:

| Priority | Score |
|---|---:|
| critical | 4 |
| high | 3 |
| medium | 2 |
| low | 1 |
| missing / unknown | 0 |

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
    score = 0   # missing or unknown
```

The `else` catching "unknown" is important: real data has typos and blanks, and your engine must not crash on them.

> **⭐ Insight — This is a tiny rules engine.** That table-turned-into-code is the same idea that powers fraud scoring, loan approvals, and support-ticket routing in real companies. The pattern — *map a category to a number, then act on the number* — scales from this five-line chain to systems handling millions of decisions a day. You're not learning a toy; you're learning the shape of business logic.

### 5. Lists: from one task to many

A **list** holds many items in order. You can read an item by its **index** (counting from `0`), measure it with `len()`, and grow it with `.append()`:

```python
tasks = ["fix login bug", "update docs", "deploy hotfix"]
print(tasks[0])        # fix login bug   (first item, index 0)
print(len(tasks))      # 3
tasks.append("review PR")
print(len(tasks))      # 4
```

> **🧠 Remember:** Lists are **zero-indexed**. The first item is `tasks[0]`, not `tasks[1]`. The last item of a 4-item list is `tasks[3]`.

### 6. Loops: `for` and `enumerate()`

A `for` loop runs the same code once per item. `enumerate()` also hands you a counter — perfect for numbered reports:

```python
tasks = ["fix login bug", "update docs", "deploy hotfix"]

for number, raw in enumerate(tasks, start=1):
    print(f"{number}. {raw.title()}")
```

Output:

```text
1. Fix Login Bug
2. Update Docs
3. Deploy Hotfix
```

You can also **count** matches as you loop:

```python
urgent_count = 0
for raw in tasks:
    if "urgent" in raw.lower():
        urgent_count += 1
print(f"Urgent tasks found: {urgent_count}")
```

### 7. Dictionaries: real task records

A list of plain strings can't hold everything we know about a task. A **dictionary** stores **key → value** pairs, so one task can carry its title, priority, status, and owner together:

```python
task = {
    "title": "  fix LOGIN bug  ",
    "priority": "critical",
    "done": False,
    "owner": "engineering",
}

print(task["title"])      # read a value by key
task["done"] = True       # update a value
```

> **💡 Why this matters:** This `{ }` shape *is* JSON. It's what APIs send and receive, what config files look like, and what database rows become in Python. Get comfortable here and Module 06 will feel like home.

### 8. `[ ]` vs `.get()` — the KeyError moment

Some tasks are missing fields. Reading a missing key with square brackets **crashes**:

```python
task = {"title": "deploy hotfix", "priority": "high", "done": False}
print(task["owner"])      # ❌ KeyError: 'owner'  — the whole script stops
```

`.get()` asks politely and lets you supply a fallback instead of crashing:

```python
print(task.get("owner", "unassigned"))   # ✅ prints: unassigned
```

> **🧠 Remember:** `task["owner"]` *demands* the key and crashes if it's missing. `task.get("owner", "unassigned")` *requests* it and falls back gracefully. At any boundary where data might be incomplete — which is always — reach for `.get()`.

> **🏭 In production:** This one-character choice — `[ ]` vs `.get()` — is the difference between a resilient service and a `500 Internal Server Error`. A single missing field with bracket access takes down the *whole* request; the same field with `.get()` and a sensible default lets the response go out clean. Production incidents are full of "it worked until one record was missing a field."

### 9. Lists of dictionaries: the real shape of data

Put it together: a **list of dictionaries** is many task records in order. Loop over it to build a report line per task:

```python
tasks = [
    {"title": "  fix LOGIN bug  ", "priority": "critical", "done": False, "owner": "engineering"},
    {"title": "Update onboarding docs", "priority": "medium", "done": False, "owner": "documentation"},
    {"title": "review pull request", "priority": "high", "done": True, "owner": "engineering"},
    {"title": "deploy hotfix", "priority": "high", "done": False},   # no owner!
]

for task in tasks:
    title = task["title"].strip().title()
    status = "done" if task["done"] else "open"
    owner = task.get("owner", "unassigned")
    print(f"{title} | {task['priority']} | {owner} | {status}")
```

Output:

```text
Fix Login Bug | critical | engineering | open
Update Onboarding Docs | medium | documentation | open
Review Pull Request | high | engineering | done
Deploy Hotfix | high | unassigned | open
```

## Suggested Visual
**Type:** Diagram
**Purpose:** Help learners see that a "list of dictionaries" is a list of boxes, where each box has labeled slots — and that `.get()` is what saves you when a slot is empty.
**Placement:** Just after Key Concept 9, before the Example Walkthrough.
**Caption:** One list, many task records — each a dictionary with labeled fields.
**What to show:** A vertical list `tasks[0] … tasks[3]`. Each element is a rounded box containing key/value rows (`title`, `priority`, `done`, `owner`). The last box (`deploy hotfix`) has the `owner` row greyed out / missing, with an arrow labeled `.get("owner", "unassigned")` pointing to a substituted value `unassigned`.

## Example Walkthrough

The companion file [code/module-01.6-example.py](../../code/module-01.6-example.py) is a runnable reference. It maps priorities to scores, detects urgent titles, stores tasks as dictionaries, and loops over a list of task dicts to print a per-task report — gracefully handling the task with a missing owner via `.get()`.

Conceptually, the flow is:

```python
# 1. score each priority (unknown → 0)
# 2. auto-escalate any title containing "urgent" to high
# 3. store tasks as a list of dictionaries
# 4. loop the list, cleaning the title and filling missing fields with .get()
# 5. print one clean report line per task
```

Run it from the project root:

```bash
python code/module-01.6-example.py
```

The companion [code/module-01.6-starter.py](../../code/module-01.6-starter.py) has `TODO`s for the scoring and urgent logic plus the list-of-dicts loop — and **one intentional bug**: a bracket access on a missing field that throws a `KeyError`. Your job is to feel the crash, then fix it with `.get()`.

## Common Mistakes or Misunderstandings

- **`=` vs `==`.** Assignment vs comparison. `if priority = "high":` is an error.
- **Off-by-one indexing.** The first item is `[0]`; a list of 4 ends at `[3]`.
- **`task["owner"]` on missing data.** This raises `KeyError` and stops everything. Use `.get("owner", "unassigned")`.
- **Forgetting `start=1` in `enumerate()`.** Without it your report numbers start at `0`.
- **Comparing against the wrong case.** `priority == "High"` fails if the data is `"high"`. Normalize first.

## Before You Start the Lab

In the lab you'll add priority scoring, urgent detection, a numbered task list, and a per-task report driven by a list of task dictionaries. Make sure you can:

- Write an `if/elif/else` chain that returns a score for every priority (including unknown).
- Loop a list with `enumerate()` to print numbered lines.
- Read fields from a dictionary with both `[ ]` and `.get()` — and know when each is safe.

---

### Short Exercise 1 — Score a priority

- **Estimated Time:** 12 min
- **Goal:** Turn the priority table into an `if/elif/else` chain.
- **Starter Context:** A variable `priority` and the score table above.
- **Task Instructions:**
  1. Write logic that sets `score` from `priority`.
  2. Make sure an unknown value (e.g. `"banana"`) yields `0`, not a crash.
  3. Print `f"{priority} → {score}"`.
- **Success Criteria:** Each of the five cases (including unknown) produces the correct score.
- **Expected Result:** e.g. `critical → 4`, `banana → 0`.
- **Optional Hint:** The final `else` is what catches missing/unknown priorities.
- **Key Takeaway:** Business rules become behavior through conditionals — and the `else` branch is your safety net for messy real-world data.

---

### Short Exercise 2 — Auto-escalate urgent tasks

- **Estimated Time:** 12 min
- **Goal:** Use `in` and Boolean logic to bump priority.
- **Starter Context:** A task dict whose title may contain `"urgent"`.
- **Task Instructions:**
  1. If the (lowercased) title contains `"urgent"`, set its priority to `"high"`.
  2. Then decide if it "needs attention": not done **and** priority is high or critical.
  3. Print a message only when it needs attention.
- **Success Criteria:** An urgent, not-done task prints the attention message; a done task does not.
- **Expected Result:** `This task needs immediate attention.`
- **Optional Hint:** `"urgent" in title.lower()` for detection; combine conditions with `and`/`or`/`not`.
- **Key Takeaway:** Keyword detection plus Boolean logic is how backends route, flag, and prioritize work automatically.

---

### Short Exercise 3 — Survive a missing field

- **Estimated Time:** 12 min
- **Goal:** Loop a list of dicts and never crash on missing data.
- **Starter Context:** A list of task dicts where one task has no `owner`.
- **Task Instructions:**
  1. Loop the list and print `Title | priority | owner | status`.
  2. Use `.get("owner", "unassigned")` for the owner.
  3. Convert `done` (True/False) into `done`/`open` text.
- **Success Criteria:** All tasks print; the owner-less task shows `unassigned`, no `KeyError`.
- **Expected Result:**
  ```text
  Fix Login Bug | critical | engineering | open
  Deploy Hotfix | high | unassigned | open
  ```
- **Optional Hint:** `"done" if task["done"] else "open"`.
- **Key Takeaway:** Real data is incomplete. `.get()` with a default is how production code stays standing when fields go missing.

---

## Using Claude Code in This Module

**When to use it:**
- **Explain** the difference between `task["owner"]` and `task.get("owner", "unassigned")`.
- **Trace** a confusing Boolean condition and tell you when it's `True`.
- **Spot** an off-by-one or `=` vs `==` mistake in your conditional.

**Prompts to try:**
1. *"Explain why `task['owner']` crashes but `task.get('owner', 'unassigned')` doesn't, with a tiny example."*
2. *"For `(priority == 'critical' or priority == 'high') and not done`, list the input combinations where this is True."*

> **Always validate.** Run your loop against the owner-less task yourself and confirm it prints `unassigned` instead of crashing.

**If Claude Code is unavailable:** Print the value just before the line that breaks (`print(task)`), then check which key is missing. The skill is reasoning about what the data actually contains — AI just speeds it up.

## Key Takeaways

- Conditionals turn plain-English business rules into program behavior.
- Combine conditions with `and`, `or`, `not`, and membership with `in`.
- The `else` branch is your safety net for unknown or missing values.
- Lists hold many ordered items; loop them with `for` and number them with `enumerate()`.
- Dictionaries model real records as key → value pairs — the shape of JSON and DB rows.
- `task["key"]` crashes on missing data; `task.get("key", default)` stays safe.

**Next:** In **Module 1.7 — Functions & the Triage Report**, you'll fold this growing-but-repetitive script into clean, reusable **functions** and assemble the full **TaskFlow Triage Report** — the finished artifact.
