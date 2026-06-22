"""TaskFlow task utilities (Module 02 reference example).

Parse and validate raw task records, score and sort them by priority, and
model a single task with a small class. Pure standard library.

Run:
    python code/module-02-example.py
"""

from __future__ import annotations


# A set is the right collection here: unique membership, O(1) lookups.
ALLOWED_PRIORITIES = {"low", "medium", "high"}
MAX_TITLE_LENGTH = 200


class InvalidTaskError(ValueError):
    """Raised when a task record is missing or has an invalid field."""


def parse_task(record: dict) -> dict:
    """Normalize a raw task record; raise InvalidTaskError on bad input."""
    title = record.get("title", "").strip()
    if not title:
        raise InvalidTaskError("Task 'title' is required")
    if len(title) > MAX_TITLE_LENGTH:
        raise InvalidTaskError(
            f"Task 'title' too long ({len(title)} > {MAX_TITLE_LENGTH})"
        )
    priority = record.get("priority", "medium").strip().lower()
    if priority not in ALLOWED_PRIORITIES:
        priority = "medium"  # forgiving default rather than rejecting
    return {"title": title, "priority": priority, "done": False}


def priority_score(priority: str) -> int:
    """Return a numeric weight for sorting tasks by priority."""
    weights = {"low": 1, "medium": 2, "high": 3}
    return weights.get(priority, 0)  # unknown -> 0, never crashes


def sort_tasks(tasks: list[dict]) -> list[dict]:
    """Return tasks ordered by priority, highest first (stable for ties)."""
    return sorted(tasks, key=lambda t: priority_score(t["priority"]), reverse=True)


def high_priority_titles(tasks: list[dict]) -> list[str]:
    """Return titles of high-priority tasks, in original order."""
    return [t["title"] for t in tasks if t["priority"] == "high"]


def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    """Append a tag to a list, creating a fresh list when none is given.

    Uses the None-sentinel pattern to avoid the mutable-default-argument trap.
    """
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


class Task:
    """A single TaskFlow task: data plus a little behavior."""

    def __init__(self, title: str, priority: str = "medium"):
        self.title = title
        self.priority = priority
        self.done = False

    def complete(self) -> None:
        """Mark the task as done."""
        self.done = True

    def __repr__(self) -> str:
        return (
            f"Task(title={self.title!r}, priority={self.priority!r}, "
            f"done={self.done})"
        )

    @classmethod
    def from_dict(cls, record: dict) -> "Task":
        """Build a Task from a raw record, validated through parse_task."""
        data = parse_task(record)
        return cls(title=data["title"], priority=data["priority"])


if __name__ == "__main__":
    raw = [
        {"title": "  Deploy ", "priority": "HIGH"},
        {"title": "Docs", "priority": "low"},
        {"title": "Hotfix", "priority": "high"},
    ]
    parsed = [parse_task(r) for r in raw]
    print("parsed:", parsed)
    print("sorted:", sort_tasks(parsed))
    print("high priority:", high_priority_titles(parsed))

    task = Task("Ship release", "high")
    print(task)
    task.complete()
    print(task)
