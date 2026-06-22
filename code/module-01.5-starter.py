"""TaskFlow triage engine — STARTER (Module 1.5).

Print the startup banner, then complete the TODOs to clean a messy title
and build a slug. A reference implementation lives in
code/module-01.5-example.py.

Run:
    python code/module-01.5-starter.py
"""

from __future__ import annotations


def clean_title(title):
    """Return a display-ready title: trimmed and Title-Cased."""
    # TODO: strip the spaces and Title-Case the words, then return the result.
    #       Hint: title.strip().title()
    raise NotImplementedError("Implement clean_title in the lab")


def slugify(title):
    """Return a URL-friendly slug like "fix-login-bug"."""
    # TODO: clean the title, lowercase it, and replace spaces with dashes.
    #       Hint: clean_title(title).lower().replace(" ", "-")
    raise NotImplementedError("Implement slugify in the lab")


if __name__ == "__main__":
    app_name = "TaskFlow"

    # 🧩 Debug/Fix: the line below is indented for no reason. Python uses
    # indentation to know what code belongs together, so this stray indent
    # crashes the script with an IndentationError. Run it, read the LAST line
    # of the traceback, then delete the extra spaces to fix it.
      print(f"Starting {app_name} Task Triage Engine...")
    print("Loaded 3 sample tasks.")
    print("Ready to analyze.")
