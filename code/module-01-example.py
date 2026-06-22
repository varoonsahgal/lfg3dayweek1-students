"""TaskFlow text utilities (Module 01 reference example).

Small, single-responsibility helpers used across TaskFlow. Pure standard library.

Run:
    python code/module-01-example.py
"""

from __future__ import annotations


def slugify_title(title: str) -> str:
    """Convert a task title into a URL-safe slug.

    Example: "  Ship the Release  " -> "ship-the-release"
    """
    return "-".join(title.strip().lower().split())


def normalize_priority(priority: str) -> str:
    """Map free-text priority to a known value, defaulting to 'medium'."""
    allowed = {"low", "medium", "high"}
    value = priority.strip().lower()
    return value if value in allowed else "medium"


def clean_title(title: str) -> str:
    """Strip surrounding whitespace and reject an empty title.

    Raises:
        ValueError: if the title is empty after stripping.
    """
    cleaned = title.strip()
    if not cleaned:
        raise ValueError("Task title cannot be empty")
    return cleaned


if __name__ == "__main__":
    # A tiny demo so the file runs on its own and shows the expected output.
    print(slugify_title("  Ship the Release  "))   # ship-the-release
    print(normalize_priority("URGENT"))            # medium
    print(clean_title("  Deploy  "))               # Deploy
