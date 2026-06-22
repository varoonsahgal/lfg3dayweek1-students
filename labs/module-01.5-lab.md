# Module 1.5 Lab — Start the TaskFlow Triage Engine

## Overview

Welcome to the Python Crash Lab. Over the next three labs you build **one** program — `app/task_triage.py` — a little "triage engine" that cleans, scores, filters, and summarizes incoming tasks. You never start over; it grows with you.

This first lab is the warm-up. You'll get the script running, lock in the rhythm every developer lives by — **edit → run → read → fix** — and ship the engine's first real feature: a **task-title cleaner** that turns `"  fix LOGIN bug  "` into a clean display title (`Fix Login Bug`) and a URL-style slug (`fix-login-bug`). You'll also read your first traceback and squash a real bug.

## Learning Objectives

By the end of this lab you will be able to:

- Run a `.py` file from the terminal and work the edit → run → read → fix loop.
- Use `print()`, variables, and f-strings to produce readable, multi-line output.
- Clean messy strings with `.strip()`, `.lower()`, `.title()`, and `.replace()`.
- Chain string methods and build a URL-style **slug** from a title.
- Read a Python traceback **last line first** and fix a typo or indentation error.

## Prerequisites

- **Module 01 complete:** a working virtual environment and the ability to run `python` from the project root.
- Basic terminal navigation (`cd`, `ls`).
- No prior Python required. If you've coded in another language, you'll move fast.
- Companion reading: [modules/module-01.5/student-handout.md](../modules/module-01.5/student-handout.md).

## Estimated Time

~45 minutes (core path). The short challenge exercises add ~30 minutes.

## Environment and Setup

```bash
cd taskflow
source .venv/bin/activate          # your prompt should show (.venv)
git checkout -b feature/triage-engine
```

You'll create and edit **`app/task_triage.py`** throughout this lab. Create it now if it doesn't exist:

```bash
touch app/task_triage.py
```

Companion code files (reference implementations, generated separately):

- [code/module-01.5-starter.py](../code/module-01.5-starter.py) — the banner with `TODO`s **plus one intentional bug** to read and fix.
- [code/module-01.5-example.py](../code/module-01.5-example.py) — a runnable warm-up + title-cleaner reference.

> **💡 Tip:** Run your file constantly with `python app/task_triage.py`. Don't try to get it perfect before running — fast feedback is the whole point.

## Scenario

TaskFlow is drowning in messy task data. Titles arrive from forms, emails, and integrations with stray spaces, random capitalization, and urgent keywords buried inside: `"  fix LOGIN bug  "`, `"URGENT: deploy hotfix"`, `"review   pull request"`. Before anyone can prioritize this work, it has to be cleaned. That's your engine's first job.

## Tasks

### Task 1: Make the engine come alive

#### Goal
Run a Python script and print the TaskFlow startup banner with f-strings.

#### 🔍 Think First (do not skip)
Before you write any code, answer these for yourself:

- An **f-string** drops a variable into text: `f"Starting {app_name}..."`. What do you think prints if you *forget* the `f` and just write `"Starting {app_name}..."`?
- You want three lines of output. Is it simpler to use three separate `print()` calls, or one giant string? (Either works — pick the one you'll understand when you re-read it tomorrow.)

#### Steps
1. Open `app/task_triage.py`.
2. Create a variable and print a three-line banner:
   ```python
   app_name = "TaskFlow"

   print(f"Starting {app_name} Task Triage Engine...")
   print("Loaded 3 sample tasks.")
   print("Ready to analyze.")
   ```
3. Run it from the project root:
   ```bash
   python app/task_triage.py
   ```

#### Checkpoint
The script runs with **no errors** and prints all three lines.

#### Expected Output
```text
Starting TaskFlow Task Triage Engine...
Loaded 3 sample tasks.
Ready to analyze.
```

> **💡 Why this matters:** Real services print exactly this kind of "I'm alive, here's what I loaded" banner at startup so engineers can confirm the app booted correctly. You just controlled a program's output — that edit → run → read loop is every workday from here on.

---

### Task 2: Clean one messy title

#### Goal
Chain string methods to turn a filthy title into a clean display title.

#### 🔍 Think First (do not skip)
You're given `raw_title = "  fix LOGIN bug  "`. You want `Fix Login Bug`.

- Which method removes the spaces on both ends?
- Which method fixes the random capitalization so each word starts with a capital?
- Method chaining runs **left to right**, each method handing its result to the next. In what order should you apply them?

**Hint:** If a chain confuses you, break it apart into one method per line, get each step right, then collapse it back together.

#### Steps
1. Add to `app/task_triage.py`:
   ```python
   raw_title = "  fix LOGIN bug  "
   clean = raw_title.strip().lower().title()
   print(f"Clean title: {clean}")
   ```
2. Run the file and confirm the title is clean.

#### Checkpoint
The messy title prints as a tidy, Title-Cased string with no leading/trailing spaces.

#### Expected Output
```text
Clean title: Fix Login Bug
```

> **💡 Why this matters:** A signup form sends `"  ALICE@Example.COM  "`; an API returns `"  Fix LOGIN Bug "`. Store that raw and you get duplicate accounts and ugly reports. The same two-line cleanup protects forms, URLs, and filenames across every backend you'll build.

---

### Task 3: Build a slug

#### Goal
Turn a clean title into a URL-friendly **slug** (`fix-login-bug`).

#### Steps
1. Below your clean title, add:
   ```python
   slug = clean.lower().replace(" ", "-")
   print(f"Slug: {slug}")
   ```
2. Run the file.

#### Checkpoint
The slug is all lowercase with dashes instead of spaces.

#### Expected Output
```text
Clean title: Fix Login Bug
Slug: fix-login-bug
```

> **🏭 In production:** Slugs show up in every blog URL (`/posts/my-first-post`), filename, and username. Learn the "lowercase and de-space" move once here, reuse it forever.

---

### Task 4: Clean a whole batch

#### Goal
Use a `for` loop to clean several messy titles at once.

#### 🔍 Think First (do not skip)
You have three messy titles to clean, not one. Rather than copy-pasting your cleanup three times, you'll loop. Look at the loop below — what value does `raw` hold on each pass?

#### Steps
1. Replace your single-title code with a batch:
   ```python
   raw_titles = ["  fix LOGIN bug ", "review   pull request", "Deploy HOTFIX  "]

   for raw in raw_titles:
       display = raw.strip().lower().title()
       slug = display.lower().replace(" ", "-")
       print(f"Clean title: {display}")
       print(f"Slug: {slug}")
   ```
2. Run the file.

#### Checkpoint
All three titles print cleaned, each with its matching slug.

#### Expected Output
```text
Clean title: Fix Login Bug
Slug: fix-login-bug
Clean title: Review   Pull Request
Slug: review---pull-request
```

> **🧪 Notice:** `"review   pull request"` has *extra* spaces in the middle, so its slug has extra dashes (`review---pull-request`). `.strip()` only trims the *ends*. That's a real-world edge case — hold onto it for the Experiment below.

---

## 🧠 Your Turn — Clean an email the same way

You've cleaned titles; now apply the exact same thinking to a different kind of messy input.

- **Goal:** Given `raw_email = "  ALICE@Example.COM  "`, produce a clean, storage-safe email: no surrounding spaces, all lowercase.
- **Constraints:** Use method chaining; print the result with an f-string; don't modify other code.
- **Expected outcome:** `Clean email: alice@example.com`.

**Hint:** Emails are case-insensitive, so you want `.strip()` and `.lower()` — but **not** `.title()` (that would wreck the address).

> **🤔 Reflect:** This is the same two lines you used on titles — and that's the point. If a signup form stores `"  ALICE@Example.COM  "` raw, then later a login form sends `"alice@example.com"`, your system sees *two different users* and the person can't log in. **Normalizing at the edge** (the instant data arrives) is what keeps that from ever happening. Notice which method you had to *leave out* — cleaning isn't one fixed recipe; it depends on the data.

Design it yourself — no full solution is provided here. (The instructor solution has a model answer.)

---

## 🧩 Debug / Fix — Read a traceback, last line first

Open [code/module-01.5-starter.py](../code/module-01.5-starter.py) and run it:

```bash
python code/module-01.5-starter.py
```

It **crashes** with a traceback. Your job is to read it and fix it.

- **Symptom:** A wall of red text ending in something like `IndentationError: unexpected indent` (or a `NameError`/`SyntaxError` from a typo).
- **Likely cause:** A stray indentation or a misspelled name in the starter banner.
- **Your task:**
  1. Read the traceback **from the bottom up** — the *last* line names the error.
  2. The line just above it points at the exact spot.
  3. Fix it and re-run until the banner prints cleanly with no red text.

**Success criteria:** The starter runs without a traceback and prints its banner.

**Hint:** The error *type* tells you what to hunt for: `IndentationError` → stray spaces at the start of a line; `NameError` → a misspelled variable; `SyntaxError` → a missing quote or parenthesis.

> **🧠 Remember:** Tracebacks are directions, not insults. Read the last line first, identify the *type*, then go to the line it points at. You don't read the whole wall — you read the bottom.

---

## Short Challenge Exercises

### Exercise A — Build the banner from variables

- **Estimated Time:** 10 min
- **Goal:** Make the banner data-driven instead of hardcoded.
- **Starter Context:** Your Task 1 banner.
- **Task Instructions:**
  1. Create `app_name = "TaskFlow"` and `task_count = 3`.
  2. Rewrite all three banner lines as f-strings that use those variables (e.g. `f"Loaded {task_count} sample tasks."`).
  3. Change `task_count` to `5` and re-run — the banner should update by itself.
- **Success Criteria:** Changing one variable updates the output; no number is hardcoded in the strings.
- **Expected Result:** `Loaded 5 sample tasks.` after the change.
- **Optional Hint:** Anything inside `{ }` in an f-string is replaced by the variable's value.
- **Key Takeaway:** Data-driven output is the foundation of every report — change the data, not the text.

### Exercise B — 🧪 Experiment: where `.strip()` stops

- **Estimated Time:** 12 min
- **Goal:** Discover the limits of `.strip()` and `.replace()` by experimenting.
- **Starter Context:** The `"review   pull request"` case from Task 4, whose slug came out as `review---pull-request`.
- **Task Instructions:**
  1. Run that title through your cleaner and confirm the triple-dash slug.
  2. Now try `.split()` on the title: `print("review   pull request".split())`. What do you get?
  3. Ask yourself: *what changed, and why?* Write a one-line comment with your answer.
- **Success Criteria:** You can explain in one sentence why `.split()` collapses the extra spaces but `.replace(" ", "-")` does not.
- **Expected Result:** `.split()` returns `['review', 'pull', 'request']` — the extra spaces are gone.
- **Optional Hint:** `.split()` with no arguments splits on *any run* of whitespace; `.replace(" ", "-")` swaps every single space one-for-one.
- **Key Takeaway:** Different tools handle messy whitespace differently — knowing which one fits the job is a real backend skill (and the seed of a cleaner slug).

### Exercise C — Slugify a tricky title

- **Estimated Time:** 12 min
- **Goal:** Produce a clean slug from a title with mixed case and punctuation.
- **Starter Context:** `raw = "Update Onboarding Docs!"`.
- **Task Instructions:**
  1. Clean it to a display title.
  2. Build a slug, then `.replace("!", "")` to drop the exclamation mark.
  3. Print both.
- **Success Criteria:** The slug is lowercase, dash-separated, and has no `!`.
- **Expected Result:** `Slug: update-onboarding-docs`.
- **Optional Hint:** You can chain another `.replace()` onto the slug to strip punctuation.
- **Key Takeaway:** Real slugs need punctuation stripped too — chaining `.replace()` calls is how you handle it without extra tools.

---

## Validation / Success Criteria

You are done when:

- [ ] `app/task_triage.py` prints the three-line startup banner with no errors.
- [ ] A messy title cleans to a Title-Cased display string.
- [ ] A slug is produced (lowercase, dashes for spaces).
- [ ] A `for` loop cleans a batch of titles (Task 4).
- [ ] You cleaned an email correctly (🧠 Your Turn).
- [ ] The starter's traceback is fixed and it runs cleanly (🧩 Debug/Fix).

**Definition of Done:** Commit `app/task_triage.py` on the `feature/triage-engine` branch and (optionally) open a merge request. Keep the commit message simple, e.g. `Start triage engine: banner + title cleaner`.

```bash
git add app/task_triage.py
git commit -m "Start triage engine: banner + title cleaner"
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Output shows literal `{app_name}` instead of `TaskFlow` | You forgot the `f` before the quotes | Use `f"...{app_name}..."` |
| `IndentationError: unexpected indent` | A stray space/tab at the start of a line | Remove leading whitespace so the line starts at column 1 |
| `NameError: name 'app_name' is not defined` | The variable is misspelled or defined *after* it's used | Define the variable above the line that uses it; check spelling |
| `python: can't open file 'app/task_triage.py'` | You're in the wrong directory | `cd` to the project root (`taskflow`) and re-run |
| The title still has stray spaces in the middle | `.strip()` only trims the **ends** | That's expected — see Exercise B; `.strip()` won't fix interior spaces |
| `.title()` produces weird capitals (e.g. `It'S`) | `.title()` capitalizes after every non-letter | Fine for this lab; note it for later, real-world edge cases |

## Stretch Goal / Extension

Add a fourth messy title of your own invention to `raw_titles` — make it as filthy as you can (extra spaces, ALL CAPS, mixed case). Run the batch and confirm your cleaner tames it. Then add a single `print()` at the top of the loop output, like `print("Cleaning titles...")`, so the section has a header. This previews the "report sections" you'll build in Module 1.7.

## Using Claude Code in This Lab

Claude Code is great for **explaining**, not doing the work for you here:

> *"Explain this traceback in plain English and tell me which line to look at: [paste the error]."*

> *"Walk me through what `\"  fix LOGIN bug  \".strip().lower().title()` produces, one method at a time."*

**Required manual verification:** Run the code yourself and confirm the output matches what you expected. AI can be confidently wrong about string edge cases.

**No-AI fallback:** Read the last line of the traceback out loud, then search the error type. Rubber-duck the method chain to a classmate, narrating what each step returns. The real skill is reasoning about input → output — AI just speeds it up.

## Key Takeaways

- Run code constantly; the edit → run → read → fix loop *is* the job.
- `print()`, variables, and f-strings are how you produce and inspect output.
- Clean strings with `.strip()`, `.lower()`, `.title()`, and `.replace()`; chain them left to right.
- Slugs and clean titles are everyday backend work, not beginner trivia.
- Read tracebacks **last line first** — they tell you exactly what broke.
- `.strip()` only trims the ends; interior whitespace needs a different tool (you'll meet it again).

**Next:** In **Module 1.6**, your engine stops cleaning *one* title and starts making *decisions* about *many* tasks — scoring priorities, flagging urgent work, and looping over lists of task dictionaries.
