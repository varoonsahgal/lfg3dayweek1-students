"""TaskFlow task utilities — STARTER (Module 02).

Complete the TODOs and FIX the mutable-default-argument bug in add_tag.
A reference implementation lives in code/module-02-example.py.

Run:
    python code/module-02-starter.py
"""

from __future__ import annotations


ALLOWED_PRIORITIES = {"low", "medium", "high"}


class InvalidTaskError(ValueError):
    """Raised when a task record is missing required fields."""


def parse_task(record: dict) -> dict:
    """Normalize a raw task record; raise InvalidTaskError on bad input."""
    # TODO: strip the title, reject empty/missing titles with InvalidTaskError,
    #       normalize priority to an allowed value, and return a clean dict
    #       shaped like {"title": ..., "priority": ..., "done": False}.
    raise NotImplementedError("Implement parse_task in the lab")


def priority_score(priority: str) -> int:
    """Return a numeric weight for sorting tasks by priority."""
    # TODO: map low/medium/high -> 1/2/3 and default unknown values to 0.
    raise NotImplementedError("Implement priority_score in the lab")


# 🧩 Debug/Fix: this function has the classic mutable-default-argument bug.
# The default list is created ONCE at definition time and shared by every call,
# so tags accumulate across separate calls.
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags


if __name__ == "__main__":
    # Demonstrate the bug: three independent calls should each return ["urgent"],
    # but the buggy version accumulates them across calls.
    print(add_tag("urgent"))   # expected: ['urgent']
    print(add_tag("urgent"))   # buggy:    ['urgent', 'urgent']
    print(add_tag("urgent"))   # buggy:    ['urgent', 'urgent', 'urgent']
