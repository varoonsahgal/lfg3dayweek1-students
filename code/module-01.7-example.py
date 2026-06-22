"""TaskFlow triage engine — Module 1.7 complete reference (task_triage.py).

The capstone of the Python Crash Lab: small single-responsibility functions
that clean, score, and filter tasks, composed into the full TaskFlow Triage
Report. Pure standard library.

Run:
    python code/module-01.7-example.py
"""

from __future__ import annotations


def clean_title(raw: str) -> str:
    """Return a display-ready title: trimmed and Title-Cased."""
    return raw.strip().title()


def priority_to_score(priority: str) -> int:
    """Map a priority word to a number (unknown/missing -> 0)."""
    if priority == "critical":
        return 4
    elif priority == "high":
        return 3
    elif priority == "medium":
        return 2
    elif priority == "low":
        return 1
    return 0


def is_attention_needed(task: dict) -> bool:
    """A task needs attention when it is NOT done AND high/critical priority."""
    not_done = not task["done"]
    urgent_priority = task["priority"] in ("high", "critical")
    return not_done and urgent_priority


def tasks_needing_attention(tasks: list[dict]) -> list[dict]:
    """Return a new list of only the tasks that need attention."""
    return [t for t in tasks if is_attention_needed(t)]


def tasks_for_owner(tasks: list[dict], owner: str) -> list[dict]:
    """Return a new list of only the tasks belonging to one owner."""
    return [t for t in tasks if t.get("owner") == owner]


def print_task_report(tasks: list[dict]) -> None:
    """Print the numbered 'All Tasks' section of the report."""
    print("All Tasks:")
    for number, task in enumerate(tasks, start=1):
        title = clean_title(task["title"])
        owner = task.get("owner", "unassigned")
        status = "done" if task["done"] else "open"
        print(f"{number}. {title} | {task['priority']} | {owner} | {status}")


if __name__ == "__main__":
    tasks = [
        {"title": "  fix LOGIN bug  ", "priority": "critical", "done": False, "owner": "engineering"},
        {"title": "update onboarding docs", "priority": "medium", "done": False, "owner": "documentation"},
        {"title": "review pull request", "priority": "high", "done": True, "owner": "engineering"},
        {"title": "deploy hotfix", "priority": "high", "done": False},  # no owner!
    ]

    # Header.
    print("TASKFLOW TRIAGE REPORT")
    print("======================")
    print()

    # All tasks, numbered.
    print_task_report(tasks)
    print()

    # Summary — every count comes from a RETURNED value, so they stay in sync.
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

    # The attention list — counted once above, printed once here.
    print("Tasks Needing Attention:")
    for task in attention:
        print(f"- {clean_title(task['title'])}")
