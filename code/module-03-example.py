"""TaskFlow utilities under test (Module 03 reference example).

These are the functions the companion pytest suite exercises. Pure standard
library so the tests stay fast and dependency-free.

Run:
    python code/module-03-example.py
Test:
    pytest code/module-03-tests.py -v
"""

from __future__ import annotations


ALLOWED_PRIORITIES = {"low", "medium", "high"}


class InvalidTaskError(ValueError):
    """Raised when a task record is missing required fields."""


def parse_task(record: dict) -> dict:
    """Normalize a raw task record; raise InvalidTaskError on bad input."""
    title = record.get("title", "").strip()
    if not title:
        raise InvalidTaskError("Task 'title' is required")
    priority = record.get("priority", "medium").strip().lower()
    if priority not in ALLOWED_PRIORITIES:
        priority = "medium"
    return {"title": title, "priority": priority, "done": False}


def priority_score(priority: str) -> int:
    """Return a numeric weight for sorting tasks by priority."""
    weights = {"low": 1, "medium": 2, "high": 3}
    return weights.get(priority, 0)


def sort_tasks(tasks: list[dict]) -> list[dict]:
    """Return tasks ordered by priority, highest first (stable for ties)."""
    return sorted(tasks, key=lambda t: priority_score(t["priority"]), reverse=True)


def high_priority_titles(tasks: list[dict]) -> list[str]:
    """Return titles of high-priority tasks, in original order."""
    return [t["title"] for t in tasks if t["priority"] == "high"]


class Task:
    """A single TaskFlow task: data plus a little behavior."""

    def __init__(self, title: str, priority: str = "medium"):
        self.title = title
        self.priority = priority
        self.done = False

    def complete(self) -> None:
        self.done = True

    def __repr__(self) -> str:
        return (
            f"Task(title={self.title!r}, priority={self.priority!r}, "
            f"done={self.done})"
        )


if __name__ == "__main__":
    print(parse_task({"title": " Ship ", "priority": "HIGH"}))
    print(priority_score("high"))
    print(high_priority_titles([
        {"title": "A", "priority": "high"},
        {"title": "B", "priority": "low"},
    ]))
