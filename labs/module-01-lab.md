# Module 01 Lab — Stand Up the TaskFlow Project

## Overview

In this lab you create the professional foundation that every later module builds on. You will scaffold the **TaskFlow** repository, isolate dependencies in a virtual environment, protect secrets, build a small utility module, and ship your first change through a Git branch and merge request. Along the way you'll use Claude Code as a reviewer — and deliberately reject a weak suggestion to practice critical review.

This is not "set up and forget." The structure and habits you build here are reused on Day 2 (databases) and Day 3 (the API). Get them right once.

Note: If you completed the student handout's short exercises that already scaffold the project and create the virtual environment, you can treat Lab Tasks 1–2 as a quick review/verification step rather than repeating them from scratch.

## Learning Objectives

By the end of this lab you will be able to:

- Scaffold a professional Python project layout (`app/`, `tests/`, config, README).
- Create and validate a virtual environment and a pinned `requirements.txt`.
- Protect secrets with `.env` and `.gitignore` from the first commit.
- Build a small, single-responsibility utility module for TaskFlow.
- Use the Git branch → commit → push → merge-request flow.
- Use Claude Code to review and refactor code, then validate the result manually.

## Prerequisites

- Python 3.11+ installed (`python3 --version`).
- Git installed (`git --version`) and a GitHub/GitLab account.
- Claude Code available (a no-AI fallback is provided).
- Basic terminal navigation (`cd`, `ls`).

## Estimated Time

~60 minutes (core path). Short challenge exercises add ~35–40 minutes.

## Environment and Setup

Work from an empty parent directory. You will create the `taskflow/` project inside it.

```bash
mkdir -p taskflow && cd taskflow
python3 --version          # confirm 3.11+
git --version              # confirm Git is available
```

Companion code files referenced by this lab (generated separately):

- `code/module-01-starter.py` — an intentionally messy script you will refactor.
- `code/module-01-example.py` — a clean reference utility module.

## Scenario

You've just joined the TaskFlow team. The "project" you inherited is a single messy script with an inline password and no structure. Your first task as the new engineer: turn it into a real project skeleton, extract a clean utility module, and put it up for review — exactly how a professional change lands on a team.

## Tasks

### Task 1: Scaffold the project skeleton

#### Goal
Create the standard TaskFlow layout with secrets ignored from the start.

#### Steps
1. From inside `taskflow/`, create the package folders and files:
   ```bash
   mkdir -p app tests
   touch app/__init__.py tests/__init__.py
   touch requirements.txt README.md .env .env.example .gitignore
   ```
2. Add to `.gitignore`:
   ```text
   .venv/
   .env
   __pycache__/
   *.pyc
   ```
3. Put a real (fake) secret in `.env` and a template in `.env.example`:
   ```text
   # .env  (NEVER committed)
   DATABASE_URL=postgresql://taskflow:supersecret@localhost:5432/taskflow

   # .env.example  (safe to commit)
   DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/taskflow
   ```
4. Initialize Git and check status:
   ```bash
   git init
   git status
   ```

#### Checkpoint
Run `git status`. The output must **not** list `.env` or `.venv/`.

#### Expected Output
```text
On branch main
No commits yet
Untracked files:
  app/
  tests/
  requirements.txt
  README.md
  .env.example
  .gitignore
```
(`.env` is absent — it is ignored.)

> **🏭 In production:** Teams back this habit with automated secret scanning (pre-commit hooks or CI checks) that block a push the moment a credential-shaped string appears. The `.gitignore` is your first line of defense, not your only one.

---

### Task 2: Isolate dependencies in a venv

#### Goal
Prove dependencies are isolated and reproducible.

#### Steps
1. Create and activate the venv:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   ```
2. Confirm you are inside it:
   ```bash
   which python                     # should point inside .venv
   ```
3. Install a dependency and pin it:
   ```bash
   pip install python-dotenv
   pip freeze > requirements.txt
   ```

#### Checkpoint
Your shell prompt shows `(.venv)` and `requirements.txt` contains `python-dotenv`.

#### Expected Output
```text
(.venv) $ cat requirements.txt
python-dotenv==1.0.1
```
(Version may differ.)

---

### Task 3: Build the TaskFlow utility module

#### Goal
Extract clean, single-responsibility functions into `app/text_utils.py`.

#### 🔍 Think First (do not skip)
Before writing code, open `code/module-01-starter.py` and read it. Answer these for yourself (in a scratch comment or out loud):

- What distinct *jobs* is this one script doing?
- Which line is a security problem?
- If a teammate had to reuse just the "make a slug from a title" logic, could they? Why not?

Write a one-sentence answer to each before continuing. This reasoning drives the refactor.

> **💡 Why this matters:** A function you can describe in one sentence is a function you can reuse and test. When a "job" takes two sentences to explain, that's the seam where it should be split into two functions.

#### Steps
1. Create `app/text_utils.py` with two single-responsibility functions:
   ```python
   def slugify_title(title: str) -> str:
       """Convert a task title into a URL-safe slug."""
       return "-".join(title.strip().lower().split())


   def normalize_priority(priority: str) -> str:
       """Map free-text priority to a known value, defaulting to 'medium'."""
       allowed = {"low", "medium", "high"}
       value = priority.strip().lower()
       return value if value in allowed else "medium"
   ```
2. Add a `__main__` demo block at the bottom so the file runs:
   ```python
   if __name__ == "__main__":
       print(slugify_title("  Ship the Release  "))
       print(normalize_priority("URGENT"))
   ```
3. Run it:
   ```bash
   python app/text_utils.py
   ```

#### Checkpoint
The module runs and prints a slug and a normalized priority.

#### Expected Output
```text
ship-the-release
medium
```

---

### Task 4: Ship a reviewable change

#### Goal
Land your work through a Git branch and a merge request.

#### Steps
1. Create a feature branch:
   ```bash
   git checkout -b feature/text-utils
   ```
2. Stage and commit a focused change:
   ```bash
   git add app/text_utils.py requirements.txt .gitignore .env.example README.md app/__init__.py tests/__init__.py
   git commit -m "Add TaskFlow text utilities and project skeleton"
   ```
3. Push and open a merge request:
   ```bash
   git push -u origin feature/text-utils
   ```
   Then open a merge/pull request targeting `main` in GitHub/GitLab with a one-sentence description.

#### Checkpoint
An open MR/PR exists from `feature/text-utils` into `main`, and `.env` is **not** in the diff.

#### Expected Output
A merge request page showing your commit, your changed files, and no `.env` file in the changes.

---

### Task 5: Claude Code review, then refactor

#### Goal
Use Claude Code to review the messy starter and validate its suggestions.

#### Steps
1. Ask Claude Code to inspect the starter:
   > *"Read `code/module-01-starter.py` and explain what it does step by step. Point out anything risky or hard to maintain."*
2. Ask for a refactor plan (signatures only, so you write the code):
   > *"Suggest how to split this script into small, single-responsibility functions. Show the function signatures only, not the implementations."*
3. **Manually verify:** Read each suggestion. Apply the ones you agree with by refactoring the starter into clean functions. Run the result.

> **Required manual verification:** Do not paste Claude Code's output in unread. Run the refactored code and confirm the behavior is unchanged before keeping it.

> **🧠 Remember:** "It runs" is not "it's correct." The only way to trust an AI refactor is to compare its output against the *original* behavior — same inputs, same outputs — not just confirm it doesn't crash.

**No-AI fallback:** Use the "Common Mistakes" checklist from the handout as a review rubric, or pair with a classmate and review each other's refactor out loud.

#### Checkpoint
The refactored script runs and produces the same output as before, but is now organized into named functions with no inline secret.

#### Expected Output
A clean, function-based version of the starter that runs without error and reads `DATABASE_URL` from the environment instead of a hardcoded string.

---

## 🧠 Your Turn — Add a third utility

You decide TaskFlow needs a helper that trims and validates a task title.

- **Goal:** Add `clean_title(title: str) -> str` to `app/text_utils.py` that strips whitespace and raises `ValueError` if the result is empty.
- **Constraints:** Single responsibility; a clear docstring; must run from the `__main__` demo.
- **Expected outcome:** `clean_title("  Deploy  ")` returns `"Deploy"`; `clean_title("   ")` raises `ValueError`.

**Hint:** A whitespace-only string is falsy after `.strip()`.

Do not look for a full solution here — design it yourself from the patterns above.

---

## 🧩 Debug / Fix — The committed secret

A teammate ran:
```bash
git add .
git commit -m "initial commit"
```
…and `.env` got committed before `.gitignore` was set up.

- **Symptom:** `git log --stat` shows `.env` in the first commit; `git status` now ignores it but it's already in history.
- **Your task:** Explain *why* simply deleting `.env` and committing again does **not** fully fix this, and describe what must change about the leaked credential.
- **Success criteria:** You can articulate that the secret lives in Git history and must be **rotated** (the password changed), not just removed from the latest commit.

**Hint:** History is forever unless rewritten — and even then, assume the secret is compromised.

---

## Short Challenge Exercises

### Exercise A — Verify the venv boundary

- **Estimated Time:** 10 min
- **Goal:** See the difference between "inside" and "outside" the venv.
- **Starter Context:** Your activated venv from Task 2.
- **Task Instructions:**
  1. With the venv active, run `which python` and `pip list`.
  2. Run `deactivate`, then `which python` again.
  3. Note how the Python path changes.
- **Success Criteria:** `which python` points inside `.venv` only when activated.
- **Expected Result:** Two different paths — one inside `.venv/bin`, one system-wide.
- **Optional Hint:** If `pip list` shows dozens of unrelated packages, you're likely outside the venv.
- **Key Takeaway:** A venv is a boundary. Knowing whether you're inside it explains most "package not found" mysteries.

### Exercise B — Write a real README

- **Estimated Time:** 12 min
- **Goal:** Make the project reproducible for a new teammate.
- **Starter Context:** The empty `README.md`.
- **Task Instructions:**
  1. Add a "Setup" section: clone, create venv, activate, `pip install -r requirements.txt`.
  2. Add a "Run" section showing `python app/text_utils.py`.
  3. Add a one-line note that `.env` must be copied from `.env.example`.
- **Success Criteria:** A teammate could set up the project using only your README.
- **Expected Result:** A README with copy-pasteable setup and run commands.
- **Optional Hint:** Use fenced code blocks so commands are easy to copy.
- **Key Takeaway:** A README is the project's front door. Reproducible setup instructions are part of the engineering deliverable, not an afterthought.

### Exercise C — Reject a weak AI suggestion

- **Estimated Time:** 12 min
- **Goal:** Practice critical review of AI output.
- **Starter Context:** Your `app/text_utils.py`.
- **Task Instructions:**
  1. Ask Claude Code: *"Refactor `slugify_title` to be 'more efficient'."*
  2. Read the suggestion critically. Does it change behavior? Reduce readability? Add complexity for no gain?
  3. Decide to accept or reject, and write one sentence justifying your decision.
- **Success Criteria:** A documented accept/reject decision with reasoning.
- **Expected Result:** Either a justified improvement or a justified rejection — not a blind paste.
- **Optional Hint:** "More efficient" rarely matters for a two-line function; readability usually wins.
- **Key Takeaway:** You own the code, not the AI. Every suggestion is reviewed, understood, and accepted or rejected on its merits.

---

## Validation / Success Criteria

You are done when:

- [ ] `git status` never lists `.env` or `.venv/`.
- [ ] The venv is active and `requirements.txt` is pinned.
- [ ] `python app/text_utils.py` runs and prints expected output.
- [ ] `clean_title` exists and behaves correctly (🧠 Your Turn).
- [ ] An open merge request targets `main` with no `.env` in the diff.
- [ ] You used Claude Code to review and manually validated the result.

**Definition of Done:** An open merge request from your feature branch into `main`, containing the project skeleton and `app/text_utils.py`, with secrets ignored.

## Troubleshooting

- **Symptom:** `pip install` succeeds but imports fail later.
  **Likely cause:** You installed outside the venv.
  **Fix:** Confirm `(.venv)` in your prompt; re-run `source .venv/bin/activate` and reinstall.

- **Symptom:** `.env` shows up in `git status`.
  **Likely cause:** `.gitignore` is missing the `.env` line or was added after staging.
  **Fix:** Add `.env` to `.gitignore`; if already staged, run `git rm --cached .env`.

- **Symptom:** `python app/text_utils.py` says "No module named app".
  **Likely cause:** You're running from the wrong directory.
  **Fix:** Run from the project root (`taskflow/`).

- **Symptom:** `git push` rejected — no remote.
  **Likely cause:** No remote configured.
  **Fix:** Create the repo on GitHub/GitLab and `git remote add origin <url>` first.

## Stretch Goal / Extension

Add a `Makefile` (or a short `scripts/setup.sh`) with `setup`, `run`, and `lint` targets so the whole team uses one command to bootstrap. Keep secrets out of it.

## Key Takeaways

- Engineering starts with structure: a consistent layout makes every later step predictable.
- Virtual environments plus a pinned `requirements.txt` make work reproducible.
- Secrets live in `.env`, git-ignored from the first commit; a leaked secret must be rotated.
- Single-responsibility functions are reusable and testable.
- Every change ships through a reviewable branch and merge request.
- Claude Code is a teammate you supervise — review, validate, accept or reject.
