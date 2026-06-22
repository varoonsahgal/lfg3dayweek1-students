"""TaskFlow utilities — STARTER with a failing test (Module 03).

priority_score below crashes on an unknown priority instead of returning 0.
Run the bundled test, read the failure, then FIX THE FUNCTION (not the test).

Test (this fails until you fix the code):
    pytest code/module-03-starter.py -v
"""


def priority_score(priority: str) -> int:
    """Return a numeric weight for sorting tasks by priority."""
    weights = {"low": 1, "medium": 2, "high": 3}
    # BUG: indexing raises KeyError for any unexpected priority value.
    # FIX: return a safe default (0) for unknown priorities, e.g. weights.get(priority, 0).
    return weights[priority]


def test_priority_score_unknown_returns_zero():
    # This test fails until priority_score handles unknown input gracefully.
    assert priority_score("unknown") == 0
