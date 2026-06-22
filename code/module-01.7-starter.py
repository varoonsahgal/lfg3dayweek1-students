"""TaskFlow triage engine — STARTER (Module 1.7).

Complete the function stubs and FIX the print-vs-return bug so the report's
counts come out right instead of None. A reference implementation lives in
code/module-01.7-example.py.

Run:
    python code/module-01.7-starter.py
"""

from __future__ import annotations


def clean_title(raw):
    """Return a display-ready title: trimmed and Title-Cased."""
    # TODO: return raw.strip().title()
    raise NotImplementedError("Implement clean_title in the lab")


def priority_to_score(priority):
    """Map a priority word to a number (unknown/missing -> 0)."""
    # TODO: if/elif/else chain returning 4/3/2/1, else 0.
    raise NotImplementedError("Implement priority_to_score in the lab")


# 🧩 Debug/Fix: this helper PRINTS its answer instead of RETURNing it. A
# function that prints throws its value away, so any caller that stores the
# result gets None — and the report's "Needs attention" count breaks. Change
# the print(...) to return ... to fix it.
def is_attention_needed(task):
    """A task needs attention when it is NOT done AND high/critical priority."""
    not_done = not task["done"]
    urgent_priority = task["priority"] in ("high", "critical")
    print(not_done and urgent_priority)  # BUG: should be `return`, not `print`


def tasks_needing_attention(tasks):
    """Return a new list of only the tasks that need attention."""
    # TODO: return [t for t in tasks if is_attention_needed(t)]
    raise NotImplementedError("Implement tasks_needing_attention in the lab")


if __name__ == "__main__":
    tasks = [
        {"title": "  fix LOGIN bug  ", "priority": "critical", "done": False, "owner": "engineering"},
        {"title": "deploy hotfix", "priority": "high", "done": False},  # no owner!
    ]

    print("TASKFLOW TRIAGE REPORT")
    print("======================")
    print()

    # Once the stubs are implemented and the print-vs-return bug is fixed,
    # this count should be 2 — not None.
    attention = tasks_needing_attention(tasks)
    print(f"Needs attention: {len(attention)}")
