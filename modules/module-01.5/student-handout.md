# Module 1.5 — Python Crash Lab: Warm-Up & Messy Text Cleanup

## Overview

The TaskFlow team has a mess on its hands. Tasks are pouring in from forms, emails, and integrations, and the titles are *filthy*: stray spaces, random capitalization, urgent keywords buried in the middle. Before anyone can prioritize this work, someone has to clean it up.

That someone is you. Across the next three short modules you'll build **one** program — `app/task_triage.py`, a little "triage engine" — that cleans, scores, filters, and summarizes incoming tasks. You never throw it away; it grows with you. By the end of the bridge it prints a real report your team could actually use.

This first module is the warm-up. You'll get the script running, learn the rhythm every developer lives by — **edit → run → read → fix** — and ship the engine's first real feature: a **task-title cleaner**. The goal isn't to memorize Python syntax. It's to start building, get fast feedback, and rack up a few quick wins.

## Why This Matters

Almost every backend you'll ever touch starts the same way: messy text comes in, clean data must go out. A signup form sends `"  ALICE@Example.COM  "`. An API returns `"  Fix LOGIN Bug "`. A file upload is named `"My Report (final)(2).pdf"`. If you store that raw, you get duplicate accounts, broken URLs, ugly reports, and unsearchable logs.

String cleanup is not a "beginner topic" you outgrow — it's a daily backend skill. The same `.strip()` and `.lower()` you learn today will be quietly protecting your database six modules from now. Learning to *run code and read its errors* is the even bigger win: that loop is how every real bug gets fixed.

## Learning Objectives

By the end of this module, you can:

- Run a `.py` file from the terminal and work the edit → run → read → fix loop.
- Use `print()`, variables, and f-strings to produce readable output.
- Read a Python error (traceback) by looking at the **last line first**.
- Fix common beginner mistakes: typos and indentation errors.
- Clean messy strings with `.strip()`, `.lower()`, `.title()`, `.replace()`, and `.split()`.
- Chain string methods together and build a URL-style **slug** from a title.

## Prerequisites

- **Module 01:** a working virtual environment and the ability to run `python` from the project root.
- Basic terminal navigation (`cd`, `ls`).
- No prior Python required. If you've coded in another language, you'll move fast.
- **Next:** this module kicks off the bridge and leads directly into **Module 1.6 — Task Decisions & Collections**, where the same `app/task_triage.py` starts making decisions about many tasks.

## Key Concepts

### 1. Running a script and the edit → run → read → fix loop

A Python program is just a text file ending in `.py`. You run it from your terminal:

```bash
python app/task_triage.py
```

That's the whole job, looped forever:

1. **Edit** the file.
2. **Run** it.
3. **Read** the output (or the error).
4. **Fix** what's wrong.
5. Run it again.

> **💡 Why this matters:** Beginners often stare at code trying to get it perfect before running it. Don't. Run it constantly. Fast feedback is how you learn what the computer actually does versus what you *think* it does.

### 2. `print()`, variables, and f-strings

`print()` shows text in the terminal. A **variable** is a labeled box that holds a value. An **f-string** (the `f` before the quotes) lets you drop variables right into text:

```python
app_name = "TaskFlow"
print(f"Starting {app_name} Task Triage Engine...")
```

Output:

```text
Starting TaskFlow Task Triage Engine...
```

Anything inside `{ }` in an f-string gets replaced with the variable's value. This is how you'll build every line of your report later.

> **🏭 In production:** Those startup banner lines aren't just for show — real services print exactly this kind of "I'm alive, here's what I loaded" message so engineers can confirm the app booted correctly.

### 3. Indentation is not decoration

Python uses **indentation** (spaces at the start of a line) to know what code belongs together. Get it wrong and Python refuses to run. We'll lean on this heavily in the next module, but for now just know: leading spaces have *meaning*.

```python
app_name = "TaskFlow"
  print(app_name)   # ❌ this stray indentation is an error
```

### 4. Reading a traceback — last line first

When Python hits a problem, it prints a **traceback**: a wall of text that looks scary but is actually a gift. The trick:

> **🧠 Remember:** Read the traceback **from the bottom up**. The *last* line names the error and usually tells you exactly what's wrong.

```text
  File "app/task_triage.py", line 2
    print(app_name)
    ^
IndentationError: unexpected indent
```

The last line says `IndentationError` — so go look at the indentation. The line above points at the exact spot. You don't read the whole thing; you read the bottom.

### 5. Strings as data: cleaning messy text

A **string** is text. Strings come with built-in tools (called **methods**) for cleaning them. The four you'll use constantly:

| Method | What it does | Example result |
|---|---|---|
| `.strip()` | removes spaces from both ends | `"  hi  "` → `"hi"` |
| `.lower()` | makes everything lowercase | `"FIX"` → `"fix"` |
| `.title()` | Capitalizes Each Word | `"fix bug"` → `"Fix Bug"` |
| `.replace(a, b)` | swaps `a` for `b` | `"a b"` → `"a-b"` |

```python
raw_title = "  fix LOGIN bug  "
clean = raw_title.strip().title()
print(clean)
```

Output:

```text
Fix Login Bug
```

> **💡 Why this matters:** `.strip()` and `.lower()` aren't cosmetic — they prevent *bugs you can't see*. To a computer, `"alice@x.com"` and `"Alice@x.com "` are two completely different strings, so a signup form that skips this step happily creates two accounts for the same person. Whitespace bugs are notorious precisely because they're **invisible**: the trailing space in `"high "` looks identical to `"high"` on screen, but `"high" == "high "` is `False`, and your priority check silently fails.

> **⭐ Insight — Normalize at the edge.** A backend mantra: *clean data the moment it enters your system, not later.* If every title, email, and username is stripped and lowercased the instant it arrives, every line of code downstream can trust it. Skip it, and the mess spreads — into your database, your logs, your search index — where it's ten times harder to fix.

### 6. Method chaining — one step at a time

The line above does three things at once. That's **method chaining**: each method hands its result to the next, left to right.

```python
raw_title = "  fix LOGIN bug  "
step1 = raw_title.strip()    # "fix LOGIN bug"
step2 = step1.lower()        # "fix login bug"
step3 = step2.title()        # "Fix Login Bug"
```

Chained together, that's just `raw_title.strip().lower().title()`. It isn't magic — it's the same three steps with the temporary variables removed.

> **🧠 Remember:** When a chain confuses you, break it back apart into one method per line. Build it up slowly until it works, then collapse it.

### 7. Building a slug with `.split()`

A **slug** is a URL-friendly version of a title: lowercase, words joined by dashes, no spaces. You'll see slugs in every blog URL (`/posts/my-first-post`). `.split()` breaks a string into a list of words, and `.replace()` (or joining) stitches them with dashes:

```python
title = "Fix Login Bug"
slug = title.lower().replace(" ", "-")
print(slug)
```

Output:

```text
fix-login-bug
```

> **💡 Why this matters:** Slugs, filenames, usernames, and search keys all need this exact "lowercase and de-space" treatment. Learn it once here, reuse it forever.

> **🏭 In production:** Slugs exist for three real reasons: **clean URLs** humans can read and share (`/posts/my-first-post` beats `/posts/8a3f9c`), **safe filenames** (no spaces or capitals to break across operating systems), and **SEO** — search engines rank readable, keyword-rich URLs higher than random IDs. One little cleanup step, three production payoffs.

## Example Walkthrough

The companion file [code/module-01.5-example.py](../../code/module-01.5-example.py) is a runnable reference. It prints the TaskFlow startup banner, then takes a batch of messy titles and turns each one into a clean **display title** and a **slug**.

Conceptually, the flow is:

```python
raw_titles = ["  fix LOGIN bug ", "URGENT: deploy hotfix", "review   pull request"]

for raw in raw_titles:
    display = raw.strip().title()          # 1. clean for humans
    slug = display.lower().replace(" ", "-")  # 2. clean for URLs
    print(f"Clean title: {display}")
    print(f"Slug: {slug}")
```

> **🔮 Peek ahead:** To keep things tidy, the actual example file wraps these two steps in two tiny named helpers, `clean_title(...)` and `slugify(...)`, using the `def` keyword. Don't worry about the mechanics yet — just read them as "the cleaning step" and "the slug step." You'll learn to write functions like these properly in **Module 1.7**; here they're only there to keep the example readable.

Run it from the project root:

```bash
python code/module-01.5-example.py
```

The companion [code/module-01.5-starter.py](../../code/module-01.5-starter.py) is your launch pad: it has the banner with `TODO`s **plus one intentional bug** (a typo/indentation mistake). Run it, read the traceback last-line-first, and fix it — that's your first real win.

## Common Mistakes or Misunderstandings

- **Reading the traceback top-down.** Read it bottom-up; the last line names the error.
- **Forgetting the `f`.** `print("Hello {name}")` prints the literal `{name}`. You need `f"..."`.
- **Mixing up `=` and `==`.** A single `=` *assigns* a value. (We'll meet `==` next module.)
- **Expecting methods to change the original.** `raw_title.strip()` returns a *new* string; it doesn't modify `raw_title`. Save the result: `clean = raw_title.strip()`.
- **Inconsistent indentation.** Pick spaces and stick with them; don't mix tabs and spaces.

## Before You Start the Lab

In the lab you'll start `app/task_triage.py` for real: print the TaskFlow startup banner, then build the title-cleaning behavior and a slug. Make sure you can:

- Run a file with `python app/task_triage.py` from the project root.
- Produce a multi-line banner with f-strings.
- Read a traceback and fix a typo or indentation error.

---

### Short Exercise 1 — Make the engine come alive

- **Estimated Time:** 10 min
- **Goal:** Run a script and produce multi-line output with f-strings.
- **Starter Context:** A fresh `app/task_triage.py` with a single banner line.
- **Task Instructions:**
  1. Create a variable `app_name = "TaskFlow"`.
  2. Use f-strings to print these three lines.
  3. Run the file from the project root.
- **Success Criteria:** The script runs with no errors and prints all three lines.
- **Expected Result:**
  ```text
  Starting TaskFlow Task Triage Engine...
  Loaded 3 sample tasks.
  Ready to analyze.
  ```
- **Optional Hint:** Three separate `print(f"...")` calls is perfectly fine.
- **Key Takeaway:** You just ran a real program and controlled its output. That edit→run→read loop is every workday from here on.

---

### Short Exercise 2 — Clean one messy title

- **Estimated Time:** 12 min
- **Goal:** Chain string methods to clean a real-looking title.
- **Starter Context:** `raw_title = "  fix LOGIN bug  "`.
- **Task Instructions:**
  1. Strip the spaces, fix the casing, and Title-Case the words.
  2. Print the clean title.
  3. Then build a slug from it.
- **Success Criteria:** Display title and slug both match the expected output exactly.
- **Expected Result:**
  ```text
  Clean title: Fix Login Bug
  Slug: fix-login-bug
  ```
- **Optional Hint:** `raw_title.strip().lower().title()` for the title; `.lower().replace(" ", "-")` for the slug.
- **Key Takeaway:** The same two-line cleanup protects forms, URLs, and filenames across every backend you'll build.

---

### Short Exercise 3 — Read a traceback and fix it

- **Estimated Time:** 10 min
- **Goal:** Turn a scary error into a quick fix.
- **Starter Context:** The intentional bug in [code/module-01.5-starter.py](../../code/module-01.5-starter.py).
- **Task Instructions:**
  1. Run the starter and read the **last line** of the traceback.
  2. Identify whether it's a typo or an indentation problem.
  3. Fix it and re-run until it's clean.
- **Success Criteria:** The starter runs without a traceback and prints its banner.
- **Expected Result:** A clean run — no red error text.
- **Optional Hint:** The error type (`SyntaxError`, `IndentationError`, `NameError`) tells you what kind of mistake to hunt for.
- **Key Takeaway:** Tracebacks are directions, not insults. Last line first, then fix.

---

## Using Claude Code in This Module

**When to use it:**
- **Explain** a traceback in plain English when the last line is unfamiliar.
- **Explain** a method chain step by step so it stops feeling like magic.
- **Suggest** which string method does a specific cleanup job.

**Prompts to try:**
1. *"Explain this traceback in plain English and tell me which line to look at: [paste the error]."*
2. *"Walk me through what `"  fix LOGIN bug  ".strip().lower().title()` produces, one method at a time."*

> **Always validate.** Run the code yourself and confirm the output matches what you expected before moving on. AI can be confidently wrong.

**If Claude Code is unavailable:** Read the last line of the traceback out loud, then search the error type. Rubber-duck the method chain to a classmate. The real skill is reasoning about input → output — AI just speeds it up.

## Key Takeaways

- Run code constantly; the edit → run → read → fix loop is the job.
- `print()`, variables, and f-strings are how you produce and inspect output.
- Read tracebacks **last line first** — they tell you exactly what broke.
- Clean strings with `.strip()`, `.lower()`, `.title()`, `.replace()`, and `.split()`.
- Chain methods left to right; break the chain apart when it confuses you.
- Slugs and clean titles are everyday backend work, not beginner trivia.

**Next:** In **Module 1.6 — Task Decisions & Collections**, your engine stops cleaning *one* title and starts making *decisions* about *many* tasks — turning business rules into code with conditionals, then scaling up with lists and dictionaries.
