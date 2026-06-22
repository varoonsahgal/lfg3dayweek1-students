# Module 1.7 — Python Crash Lab: Functions & the Triage Report

## Overview

Your triage engine *works* — but look at it. The title-cleaning logic is copy-pasted in three places. The scoring `if/elif` chain shows up wherever you need a number. Every time the team asks for a tweak, you change the same thing in five spots and miss one. The script is doing real work, but it's a tangle.

This module is the cure. You'll learn **functions** — named, reusable chunks of logic — and use them to fold all that duplication into a handful of clean, single-purpose tools: `clean_title`, `priority_to_score`, `is_attention_needed`, and `print_task_report`. Then you'll add two **filter helpers** (`tasks_needing_attention`, `tasks_for_owner`) and snap everything together into the finished **TaskFlow Triage Report**.

This is the capstone of the Python Crash Lab. When you're done, `app/task_triage.py` won't look like a beginner's script anymore — it'll look like the start of real application code, and it's the perfect on-ramp to Module 02.

## Why This Matters

Functions are *the* unit of backend engineering. Every API endpoint, every database helper, every validation rule you write from here on is a function. They matter for three reasons: **reuse** (write once, call everywhere), **readability** (a name like `is_attention_needed(task)` documents itself), and **testability** (a function with clear inputs and outputs is something you can prove correct — which is literally Module 03's job).

The single most important idea in this module — **print vs. return** — is also the one beginners get wrong most. A function that *prints* throws its result away; a function that *returns* hands you a value you can reuse. Your final report is built by *composing* functions, and you can only compose functions that return.

## Learning Objectives

By the end of this module, you can:

- Write functions with `def`, parameters, arguments, and `return` values.
- Explain the difference between **printing** and **returning** — and choose correctly.
- Extract repeated logic into small, single-responsibility functions.
- Write filter functions that return a subset of tasks.
- Compose functions to assemble the complete TaskFlow Triage Report.

## Prerequisites

- **Module 1.5:** string cleanup, f-strings, and the edit → run → read → fix loop.
- **Module 1.6:** conditionals, Boolean logic, lists, dictionaries, and lists of dictionaries.
- A working `app/task_triage.py` that cleans titles, scores priorities, and loops over task dicts.
- **Next:** this module leads into **Module 02 — Python Fundamentals**, the applied/intermediate Python module covering classes, exceptions, and modules.

## Key Concepts

### 1. `def`: defining a function

A **function** is a named, reusable block of code. You **define** it with `def`, give it **parameters** (inputs), and **call** it later with **arguments** (actual values):

```python
def clean_title(raw):           # 'raw' is a parameter
    return raw.strip().title()

result = clean_title("  fix LOGIN bug  ")   # "  fix LOGIN bug  " is an argument
print(result)                                # Fix Login Bug
```

> **🧠 Remember:** **Parameter** = the name in the definition (`raw`). **Argument** = the real value you pass in when calling (`"  fix LOGIN bug  "`). Same slot, two names depending on which side you're on.

### 2. `return` values — the heart of reuse

`return` sends a value *back to whoever called the function*. That returned value can be stored, passed to another function, or dropped into your report:

```python
def priority_to_score(priority):
    if priority == "critical":
        return 4
    elif priority == "high":
        return 3
    elif priority == "medium":
        return 2
    elif priority == "low":
        return 1
    return 0                      # missing or unknown

score = priority_to_score("high")    # score is now 3
total = score + priority_to_score("critical")   # reuse it: 3 + 4 = 7
```

Because each call hands back a number, you can do math with the results. That's reuse.

### 3. Print vs. return — the bug that bites everyone

This is the most important idea in the module. Watch the difference:

```python
# ❌ This PRINTS — the value escapes to the screen and is gone
def score_bad(priority):
    print(priority_to_score(priority))

# ✅ This RETURNS — the value comes back so you can use it
def score_good(priority):
    return priority_to_score(priority)

x = score_bad("high")     # prints 3, but x is None!  Nothing came back.
y = score_good("high")    # y is 3 — usable in the report
```

> **💡 Why this matters:** A function that prints can put text on the screen, but it **can't hand its result to your report**. The total/completed/open counts at the end are built by *adding up returned values*. If `is_attention_needed` printed `True` instead of returning it, you could never count how many tasks need attention. **Print is for showing a human. Return is for feeding the rest of your program.**

> **🧠 Remember:** If another part of your code needs the answer, **return** it. Only `print()` at the very end, when a human is the audience.

### 4. Single-responsibility functions

Each function should do **one** thing. That makes it easy to name, reuse, and reason about:

```python
def clean_title(raw):
    """Return a display-ready title."""
    return raw.strip().title()

def is_attention_needed(task):
    """A task needs attention when it's NOT done AND high/critical priority."""
    not_done = not task["done"]
    urgent_priority = task["priority"] in ("high", "critical")
    return not_done and urgent_priority
```

Notice `is_attention_needed` **returns a Boolean** (`True`/`False`). That's deliberate — you'll *count* those Trues later.

> **🏭 In production:** Small, single-purpose functions are what make a codebase changeable. When the "needs attention" rule changes, you edit *one* function and every part of the app that uses it updates at once.

### 5. Filter functions: returning a subset

A **filter** loops a list and returns only the items that match. Two you'll build:

```python
def tasks_needing_attention(tasks):
    return [t for t in tasks if is_attention_needed(t)]

def tasks_for_owner(tasks, owner):
    return [t for t in tasks if t.get("owner") == owner]
```

> **🧠 Remember:** These return *new lists*. The original `tasks` list is untouched, so you can filter it many different ways without breaking anything.

You don't have to use the bracket shorthand — a plain loop with `.append()` is just as valid:

```python
def tasks_needing_attention(tasks):
    result = []
    for t in tasks:
        if is_attention_needed(t):
            result.append(t)
    return result
```

### 6. Composing functions into the final report

The payoff: small functions snap together. `print_task_report` and a summary section *use* the functions above to build the finished report:

```python
def print_task_report(tasks):
    print("All Tasks:")
    for number, task in enumerate(tasks, start=1):
        title = clean_title(task["title"])
        owner = task.get("owner", "unassigned")
        status = "done" if task["done"] else "open"
        print(f"{number}. {title} | {task['priority']} | {owner} | {status}")
```

And the summary counts come straight from your filter and returned values:

```python
total = len(tasks)
completed = len([t for t in tasks if t["done"]])
open_count = total - completed
attention = tasks_needing_attention(tasks)
```

Because every helper **returns**, the report is just gluing returned values together with f-strings.

> **🏭 In production:** This report isn't make-believe \u2014 it's the skeleton of every ops dashboard and on-call triage tool. A real incident page does the exact same thing: pull a list of records, score them, *filter to the ones that need a human right now*, and show counts at the top. Swap `tasks` for alerts, support tickets, or failing health-checks and you have a monitoring tool. The shape you're building here is the shape teams stare at all day.

## Suggested Visual
**Type:** Flowchart
**Purpose:** Show how small returning functions feed into the final report — making "compose returned values" concrete.
**Placement:** Just before the Example Walkthrough.
**Caption:** Small functions return values; the report composes them.
**What to show:** Left column of function boxes (`clean_title`, `priority_to_score`, `is_attention_needed`, `tasks_needing_attention`, `tasks_for_owner`) each with an arrow labeled "returns a value" pointing right into a single box `Build TASKFLOW TRIAGE REPORT`, which outputs the final report text. Contrast a greyed-out `print()`-only box with a broken arrow labeled "nothing returned → can't compose."

## Example Walkthrough

The companion file [code/module-01.7-example.py](../../code/module-01.7-example.py) is the **complete reference** `task_triage.py`. It defines `clean_title`, `priority_to_score`, `is_attention_needed`, the two filter helpers, and `print_task_report`, then assembles the full report for a list of task dictionaries.

Run it from the project root:

```bash
python code/module-01.7-example.py
```

Expected output — the finished artifact:

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

The companion [code/module-01.7-starter.py](../../code/module-01.7-starter.py) has function stubs with `TODO`s — **including one intentional print-vs-return bug**: a helper that `print()`s its result instead of returning it, so the report's counts come out wrong (or as `None`). Finding and fixing that bug is the centerpiece of the lab.

## Common Mistakes or Misunderstandings

- **Printing instead of returning.** If the report needs the value, `return` it. Printing throws it away.
- **Forgetting the `return` keyword.** A function with no `return` hands back `None` silently.
- **Confusing parameters and arguments.** Parameters are in the `def`; arguments are what you pass in.
- **Re-implementing logic instead of calling a function.** If you already wrote `clean_title`, *call it* — don't paste the `.strip().title()` again.
- **Mutating the original list when filtering.** Build and return a *new* list; leave the input alone.

## Before You Start the Lab

In the lab you'll refactor your script into functions and then build the full triage report. Make sure you can:

- Write a function that **returns** a value and call it, storing the result.
- Explain out loud why a printing function can't feed the report's counts.
- Build a filtered list with either a comprehension or a `for`/`append` loop.
- Compose `clean_title`, `priority_to_score`, `is_attention_needed`, and the filters into one report.

---

### Short Exercise 1 — Extract `clean_title`

- **Estimated Time:** 10 min
- **Goal:** Turn copy-pasted cleanup into one reusable function.
- **Starter Context:** Your script cleans titles inline in two or more places.
- **Task Instructions:**
  1. Define `clean_title(raw)` that **returns** the cleaned title.
  2. Replace every inline cleanup with a call to `clean_title(...)`.
  3. Confirm the report output is unchanged.
- **Success Criteria:** No more duplicated `.strip().title()` chains; output identical to before.
- **Expected Result:** `clean_title("  fix LOGIN bug  ")` → `Fix Login Bug`.
- **Optional Hint:** Write the function once, then delete the duplicates one at a time, re-running after each.
- **Key Takeaway:** A function is "write once, call everywhere." When the cleanup rule changes, you'll edit exactly one place.

---

### Short Exercise 2 — Fix the print-vs-return bug

- **Estimated Time:** 12 min
- **Goal:** Make the difference between print and return unforgettable.
- **Starter Context:** The buggy helper in [code/module-01.7-starter.py](../../code/module-01.7-starter.py) that prints instead of returns.
- **Task Instructions:**
  1. Run the starter and watch the summary counts come out wrong (or `None`).
  2. Find the helper that `print()`s instead of `return`s.
  3. Change it to `return`, then re-run.
- **Success Criteria:** The summary counts are correct after the fix.
- **Expected Result:** `Needs attention: 2` (not `None` or `0`).
- **Optional Hint:** A function whose result you store but that uses `print()` will leave your variable as `None`.
- **Key Takeaway:** Print is for humans; return is for your program. Composable reports require returning values.

---

### Short Exercise 3 — Build a filter and use it

- **Estimated Time:** 15 min
- **Goal:** Write a filter function and feed its result into the report.
- **Starter Context:** Your list of task dicts and `is_attention_needed`.
- **Task Instructions:**
  1. Write `tasks_needing_attention(tasks)` that **returns** a list.
  2. Use its length for the `Needs attention:` count.
  3. Loop its result to print the `Tasks Needing Attention:` section.
- **Success Criteria:** The count and the listed titles agree with each other and the expected output.
- **Expected Result:**
  ```text
  Tasks Needing Attention:
  - Fix Login Bug
  - Deploy Hotfix
  ```
- **Optional Hint:** A task needs attention when `not task["done"]` **and** its priority is `"high"` or `"critical"`.
- **Key Takeaway:** Filters return reusable subsets — one list, counted once and printed once, always in sync.

---

## Using Claude Code in This Module

**When to use it:**
- **Spot** print-vs-return mistakes and explain why a value came back as `None`.
- **Suggest** how to split a long function into smaller single-responsibility ones.
- **Refactor** repeated logic into a function (then *you* verify the output matches).

**Prompts to try:**
1. *"My function stores a value but it's `None`. Here's the code — is this a print-vs-return bug? [paste function]."*
2. *"Suggest how to break this long report function into smaller single-responsibility functions, but keep the output identical."*

> **Always validate.** Run the script and compare against the expected TASKFLOW TRIAGE REPORT line by line. If a refactor changes the output, revert and investigate before accepting.

**If Claude Code is unavailable:** Add `print(repr(value))` right after a function call to see what actually came back. If it's `None`, you have a print-vs-return bug. The skill is reasoning about inputs and outputs — AI just speeds it up.

## Key Takeaways

- Functions (`def`, parameters, arguments, `return`) are the core unit of backend code.
- **Return** values when your program needs them; **print** only for humans at the end.
- A function that prints can't feed the report — composition requires returning.
- Extract repeated logic into small, single-responsibility functions.
- Filters return reusable subsets so counts and lists stay in sync.
- Composing returning functions is how the full triage report is assembled.

**Next:** In **Module 02 — Python Fundamentals** (the applied, intermediate Python module), you'll take these very functions further with comprehensions, custom exceptions, importable modules, and your first classes — turning `task_triage.py` into testable, production-style code.
