"""TaskFlow triage engine — Module 1.5 reference example.

Warm-up: print the startup banner, then turn a batch of messy task titles
into a clean display title and a URL-style slug. Pure standard library.

Run:
    python code/module-01.5-example.py
"""

from __future__ import annotations


def clean_title(title: str) -> str:
    """Return a display-ready title: trimmed and Title-Cased.

    ".strip()" removes the stray spaces from both ends; ".title()" gives
    each word a capital letter so the report looks tidy for humans.
    """
    return title.strip().title()


def slugify(title: str) -> str:
    """Return a URL-friendly slug like "fix-login-bug".

    Clean the title first, lowercase it, then swap spaces for dashes.
    Slugs show up in every blog URL and filename you will ever build.
    """
    cleaned = clean_title(title)
    return cleaned.lower().replace(" ", "-")


if __name__ == "__main__":
    # 1. Startup banner — f-strings drop variables straight into text.
    app_name = "TaskFlow"
    sample_count = 3
    print(f"Starting {app_name} Task Triage Engine...")
    print(f"Loaded {sample_count} sample tasks.")
    print("Ready to analyze.")
    print()

    # 2. A batch of realistically messy titles from forms, emails, and APIs.
    raw_titles = [
        "  fix LOGIN bug  ",
        "URGENT: deploy hotfix",
        "review   pull request",
    ]

    # 3. Clean each one for humans (title) and for URLs (slug).
    for raw in raw_titles:
        display = clean_title(raw)
        slug = slugify(raw)
        print(f"Clean title: {display}")
        print(f"Slug: {slug}")
