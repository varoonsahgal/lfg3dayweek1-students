"""TaskFlow triage engine — Module 1.6 reference example.

Make decisions about many tasks: score each priority, auto-detect "urgent"
titles, and loop over a list of task dictionaries to print a per-task report
that survives a missing field. Pure standard library.

Run:
    python code/module-01.6-example.py
"""

from __future__ import annotations


def priority_to_score(priority: str) -> int:
    """Map a priority word to a number so tasks can be compared.

    Unknown or missing priorities fall through to 0 so the engine never
    crashes on messy real-world data.
    """
    if priority == "critical":
        return 4
    elif priority == "high":
        return 3
    elif priority == "medium":
        return 2
    elif priority == "low":
        return 1
    else:
        return 0  # missing or unknown


if __name__ == "__main__":
    # A list of dictionaries — the JSON-like shape APIs and databases use.
    # Note the last task has NO "owner" key on purpose.
    tasks = [
        {"title": "  fix LOGIN bug  ", "priority": "critical", "done": False, "owner": "engineering"},
        {"title": "Update onboarding docs", "priority": "medium", "done": False, "owner": "documentation"},
        {"title": "review pull request", "priority": "high", "done": True, "owner": "engineering"},
        {"title": "URGENT: deploy hotfix", "priority": "medium", "done": False},  # no owner!
    ]

    print("Per-task report:")
    urgent_count = 0

    for task in tasks:
        title = task["title"].strip().title()

        # Auto-escalate: any title containing "urgent" jumps to high priority.
        priority = task["priority"]
        if "urgent" in task["title"].lower():
            priority = "high"
            urgent_count += 1

        score = priority_to_score(priority)
        status = "done" if task["done"] else "open"
        # .get() asks politely and falls back instead of raising KeyError.
        owner = task.get("owner", "unassigned")

        print(f"{title} | {priority} (score {score}) | {owner} | {status}")

    print()
    print(f"Urgent tasks found: {urgent_count}")
