"""TaskFlow triage engine — STARTER (Module 1.6).

Complete the TODOs for scoring, urgent detection, and the per-task loop, then
FIX the KeyError bug on the task that is missing an "owner". A reference
implementation lives in code/module-01.6-example.py.

Run:
    python code/module-01.6-starter.py
"""

from __future__ import annotations


def priority_to_score(priority):
    """Map a priority word to a number (critical=4 ... low=1, unknown=0)."""
    # TODO: write an if/elif/else chain that returns 4/3/2/1, with a final
    #       else that returns 0 for missing or unknown priorities.
    raise NotImplementedError("Implement priority_to_score in the lab")


if __name__ == "__main__":
    tasks = [
        {"title": "  fix LOGIN bug  ", "priority": "critical", "done": False, "owner": "engineering"},
        {"title": "URGENT: deploy hotfix", "priority": "medium", "done": False},  # no owner!
    ]

    for task in tasks:
        title = task["title"].strip().title()

        # TODO: if the lowercased title contains "urgent", bump priority to "high".

        status = "done" if task["done"] else "open"

        # 🧩 Debug/Fix: this uses square brackets to read "owner". The second
        # task has no "owner" key, so this line raises KeyError and stops the
        # script. Fix it by switching to task.get("owner", "unassigned").
        owner = task["owner"]

        print(f"{title} | {task['priority']} | {owner} | {status}")
