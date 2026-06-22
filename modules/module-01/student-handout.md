# Module 01 — Engineering Mindset, Project Setup, Git & Claude Code Workflow

## Overview

Welcome to TaskFlow. Over the next three days you will build one real backend service — a task manager — and grow it from a folder of utility functions into a tested, database-backed REST API. This first module is where you stop "writing scripts" and start "engineering applications."

That distinction is the whole point of today. A script runs once on your machine and is forgotten. An engineered application is structured, version-controlled, reviewed by teammates, tested, and safe to change six months from now. Every habit you build in this module — project layout, virtual environments, secrets handling, Git branches, and disciplined use of Claude Code — is a habit professional teams expect on day one of the job.

Keep this mindset: **you are the engineer; Claude Code is a fast, knowledgeable teammate whose work you always review.**

## Why This Matters

Most bugs, outages, and security incidents in real teams trace back to missing fundamentals, not exotic problems: a secret committed to Git, a dependency that "worked on my machine," a change nobody could review, or code nobody tested. The structure you set up today is your defense against all of that. Setting it up correctly once means every later module — Python modules, tests, databases, APIs — drops cleanly into place.

## Learning Objectives

By the end of this module, you can:

- Explain the difference between writing scripts and engineering maintainable applications.
- Create a professional Python project structure (app folder vs. test folder, config, README).
- Create and use a virtual environment and a `requirements.txt`.
- Manage local secrets with `.env` and protect them with `.gitignore`.
- Use Git branches, commits, and merge requests, and explain why teams never commit directly to `main`.
- Use Claude Code to explain code, suggest refactors, and review a file — then validate the output manually.

## Prerequisites

- Basic terminal navigation: `cd`, `ls`, running a command.
- Python 3.11+ installable, Git installed, a GitHub/GitLab account, and Claude Code available.
- No prior experience with project structure, testing, databases, or APIs is assumed.

## Key Concepts

### 1. Scripts vs. engineered applications

A **script** is a single file you run top-to-bottom. It is great for a one-off calculation. An **engineered application** is built to be read, changed, tested, and shared by a team over time. The difference is not size — it's intent.

| Script mindset | Engineering mindset |
|---|---|
| "It runs on my laptop." | "It runs anywhere, reproducibly." |
| One big file | Small, single-responsibility modules |
| Secrets pasted inline | Secrets in `.env`, never committed |
| No tests | Tested, so changes are safe |
| Edit `main` directly | Branch → review → merge |

> **Callout — Why start here?** Maintainability, testing, security, and deployment are *cheaper* when designed in early and *painful* when bolted on later. We pay the small cost now.

> **🏭 In production:** The "throwaway" script almost never stays throwaway — a useful one gets copied, scheduled as a cron job, and depended on by teammates within weeks. Building it like a service from the start is cheaper than retrofitting structure after it has quietly become load-bearing.

### 2. The TaskFlow project layout

You will create this structure today and reuse it all course long:

```text
taskflow/
├── app/                # application code (your modules live here)
│   └── __init__.py
├── tests/              # pytest tests live here (Module 03)
│   └── __init__.py
├── .env                # local secrets — NEVER committed
├── .env.example        # template showing required keys (safe to commit)
├── .gitignore          # tells Git what to ignore (includes .env)
├── requirements.txt    # pinned dependencies
└── README.md           # how to set up and run the project
```

Separating `app/` from `tests/` keeps production code and test code clearly distinct. The `__init__.py` files mark these folders as Python packages so you can import across them later.

### 3. Virtual environments and dependency isolation

A **virtual environment** ("venv") is a private, project-local copy of Python and its packages. Without it, every project shares one global Python and dependencies collide ("works on my machine" disease). With it, each project pins exactly what it needs.

```bash
# Create and activate a venv (run from the project root)
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows PowerShell

# Confirm you are inside the venv
which python                     # should point inside .venv

# Record dependencies so teammates can reproduce them
pip install python-dotenv
pip freeze > requirements.txt
```

> **Callout — Activation is the #1 setup snag.** If imports or commands behave strangely, check that your prompt shows `(.venv)`. Re-run the `source` command if not.

### 4. Secrets and `.gitignore`

Secrets (database passwords, API keys) belong in a local `.env` file that is **never** committed. You commit a `.env.example` instead, which lists the *keys* but not the *values*.

```text
# .env  (committed? NO)
DATABASE_URL=postgresql://taskflow:supersecret@localhost:5432/taskflow

# .env.example  (committed? YES)
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/taskflow
```

```text
# .gitignore
.venv/
.env
__pycache__/
*.pyc
```

> **Secure-coding callout:** A committed secret is a permanent secret — it lives in Git history even after you delete the file. Protect `.env` from the very first commit.

> **🧠 Remember:** Once a secret reaches a shared remote, deleting it is not enough — you must *rotate* it (change the password or key). Assume any credential that ever touched Git history is already compromised.

### 5. Git workflow: branch → commit → push → merge request

Professional teams protect `main` and change it only through reviewed **merge requests** (MRs, also called pull requests). The flow:

```bash
git checkout -b feature/slugify-util   # 1. branch off main
# ... make changes ...
git add app/text_utils.py
git commit -m "Add slugify_title utility"   # 2. commit a focused change
git push -u origin feature/slugify-util      # 3. push the branch
# 4. Open a merge request in GitHub/GitLab → request review → merge
```

> **Callout — Why never commit to `main`?** Because every change deserves a second set of eyes. Branches make work reviewable, reversible, and safe.

## Example Walkthrough

The companion file `code/module-01-example.py` is a small, readable TaskFlow utility module. Conceptually it contains single-responsibility functions like:

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

Notice each function does *one* thing, names its inputs and output, and is easy to test later. Run the example from the project root:

```bash
python code/module-01-example.py
```

You should see a short demo printout from its `__main__` block. The companion `code/module-01-starter.py` is an intentionally messy script — one giant block with inline secrets and no functions — that you will refactor in the lab into clean, single-responsibility code.

## Common Mistakes or Misunderstandings

- **Forgetting to activate the venv.** Packages "disappear" or install globally. Look for `(.venv)` in your prompt.
- **Committing `.env`.** Add it to `.gitignore` *before* your first commit.
- **Giant commits.** Commit focused, logical changes with clear messages.
- **Editing `main` directly.** Always branch.
- **Accepting Claude Code output blindly.** Read it, understand it, then keep or reject it.

## Before You Start the Lab

Verify your environment:

```bash
python3 --version          # 3.11 or higher
git --version              # any recent version
source .venv/bin/activate  # prompt shows (.venv)
```

In the lab you will: create the TaskFlow repo and layout, set up the venv and `requirements.txt`, add `.env`/`.env.example`/`.gitignore`, build a utility module, branch, commit, open a merge request, and use Claude Code to review a file before refactoring.

---

### Short Exercise 1 — Scaffold the TaskFlow project

- **Estimated Time:** 12 min
- **Goal:** Create a professional project skeleton from scratch.
- **Starter Context:** An empty folder named `taskflow/`.
- **Task Instructions:**
  1. Create `app/` and `tests/`, each with an empty `__init__.py`.
  2. Add `requirements.txt`, `README.md`, `.env`, `.env.example`, and `.gitignore`.
  3. Put `.venv/` and `.env` in `.gitignore`.
  4. Run `git init`, then `git status`.
- **Success Criteria:** `git status` does **not** list `.env` or `.venv/` as files to track.
- **Expected Result:** A clean tree matching the layout above, with secrets and the venv ignored.
- **Optional Hint:** `cat .gitignore` to confirm its contents before checking `git status`.
- **Key Takeaway:** Structure is a feature. A consistent layout makes every later step — imports, tests, config — predictable, and ignoring secrets from the first commit prevents an unfixable security mistake.

---

### Short Exercise 2 — Isolate dependencies with a venv

- **Estimated Time:** 10 min
- **Goal:** Prove that dependencies are isolated and reproducible.
- **Starter Context:** The project from Exercise 1.
- **Task Instructions:**
  1. Create and activate a venv (`python3 -m venv .venv` then `source .venv/bin/activate`).
  2. `pip install python-dotenv`.
  3. Run `pip freeze > requirements.txt` and open the file.
  4. Deactivate (`deactivate`) and run `which python` — note the difference.
- **Success Criteria:** `requirements.txt` lists `python-dotenv`; `which python` points inside `.venv` only while activated.
- **Expected Result:** A pinned dependency list and a clear sense of "inside vs. outside" the venv.
- **Optional Hint:** If `python-dotenv` doesn't appear, you likely installed it before activating.
- **Key Takeaway:** Reproducible environments are how teams avoid "works on my machine." `requirements.txt` is the contract that lets anyone rebuild your exact setup.

---

### Short Exercise 3 — Make your first reviewable change

- **Estimated Time:** 15 min
- **Goal:** Practice the branch → commit → push → merge-request flow.
- **Starter Context:** The TaskFlow repo, pushed to GitHub/GitLab.
- **Task Instructions:**
  1. Create a branch `feature/readme-setup`.
  2. Add setup and run instructions to `README.md`.
  3. Commit with a clear message and push the branch.
  4. Open a merge request and write a one-sentence description.
- **Success Criteria:** An open MR exists targeting `main` from your feature branch.
- **Expected Result:** A small, reviewable change ready for a teammate's eyes — `main` untouched directly.
- **Optional Hint:** Keep the commit message in the imperative mood: "Add setup instructions."
- **Key Takeaway:** Every change being reviewable is what makes a codebase safe to evolve. The MR is the unit of collaboration, not the commit.

---

## Using Claude Code in This Module

Use Claude Code as a reviewer and planner today — not to generate the whole project for you.

**When to use it:**
- **Inspect** the messy starter script and ask what it does before you touch it.
- **Plan** a refactor into single-responsibility functions.
- **Review** a file for readability and obvious mistakes.

**Prompts to try:**
1. *"Read `code/module-01-starter.py` and explain what it does, step by step. Point out anything that looks risky or hard to maintain."*
2. *"Suggest how to split this script into small, single-responsibility functions. Show the function signatures only, not the full implementation, so I can write them myself."*

> **Always validate.** Read every suggestion. If Claude Code proposes something you don't understand or disagree with, reject it and ask why. In the lab you will deliberately reject a weak suggestion to practice critical review.

> **⚖️ Tradeoff:** Claude Code trades your time for its speed — but never your accountability. A reviewer who rubber-stamps AI output is slower in the long run, because every unreviewed bug returns as a production incident with your name on the commit.

**If Claude Code is unavailable:** Pair with a classmate and review each other's starter-script refactor out loud, or use the "Common Mistakes" checklist above as a manual review rubric. The skill is *structured review*, with or without AI.

## Key Takeaways

- Engineering ≠ scripting: structure, isolation, secrets hygiene, and review are non-negotiable.
- A consistent project layout makes everything later easier.
- Virtual environments + `requirements.txt` make your work reproducible.
- Secrets live in `.env` and are git-ignored from the first commit.
- All change flows through branches and reviewed merge requests.
- Claude Code is a teammate you supervise, never an autopilot.

**Next:** If you're new to Python, the **Python Crash Lab bridge (Modules 1.5–1.7)** comes next — you'll build `app/task_triage.py`, a small triage engine, to get fluent with Python basics before the faster tour. (Confident Python users can skip straight ahead.) Then **Module 02 — Python Fundamentals for Backend Development** fills that clean `app/` folder with idiomatic Python: collections, functions, modules, error handling, and a small `Task` class — the building blocks of TaskFlow's logic.
