"""Pytest suite for the Module 03 example (TaskFlow utilities).

Demonstrates Arrange-Act-Assert, a fixture, parametrization, and pytest.raises.
The example module's filename contains hyphens, so we load it by path with
importlib rather than a normal import.

Test:
    pytest code/module-03-tests.py -v
"""

import importlib.util
import os

import pytest


def _load(filename, module_name):
    path = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tu = _load("module-03-example.py", "module_03_example")


@pytest.fixture
def sample_tasks():
    """Shared task data so tests don't repeat setup."""
    return [
        {"title": "Deploy", "priority": "high", "done": False},
        {"title": "Docs", "priority": "low", "done": False},
        {"title": "Hotfix", "priority": "high", "done": False},
    ]


def test_parse_task_valid_returns_normalized():
    # Arrange
    record = {"title": " Ship ", "priority": "HIGH"}
    # Act
    result = tu.parse_task(record)
    # Assert
    assert result == {"title": "Ship", "priority": "high", "done": False}


def test_parse_task_missing_title_raises():
    with pytest.raises(tu.InvalidTaskError):
        tu.parse_task({})


def test_parse_task_whitespace_title_raises():
    with pytest.raises(tu.InvalidTaskError):
        tu.parse_task({"title": "   "})


@pytest.mark.parametrize("priority, expected", [
    ("low", 1),
    ("medium", 2),
    ("high", 3),
    ("unknown", 0),   # boundary / unexpected input
])
def test_priority_score_mapping(priority, expected):
    assert tu.priority_score(priority) == expected


def test_high_priority_filter(sample_tasks):
    assert tu.high_priority_titles(sample_tasks) == ["Deploy", "Hotfix"]


def test_sort_tasks_orders_high_to_low(sample_tasks):
    ordered = tu.sort_tasks(sample_tasks)
    scores = [tu.priority_score(t["priority"]) for t in ordered]
    assert scores == sorted(scores, reverse=True)


def test_task_complete_sets_done_true():
    task = tu.Task("Ship release", "high")
    assert task.done is False
    task.complete()
    assert task.done is True
