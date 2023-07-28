import pytest
from tinyagi.context.actions import build_actions_context, get_context_builders


def test_build_actions_context():
    # Test with a context that should have results.
    context = build_actions_context({"summary": "some relevant text"})
    assert "available_actions" in context
    assert "available_short_actions" in context
    assert isinstance(context["available_actions"], str)
    assert isinstance(context["available_short_actions"], str)
    # Make sure some actions are returned.
    assert len(context["available_actions"]) > 0

    # Test with a context that should not have any results.
    context = build_actions_context({"summary": "nonexistent action"})
    assert "available_actions" in context
    assert "available_short_actions" in context
    assert isinstance(context["available_actions"], str)
    assert isinstance(context["available_short_actions"], str)
    # Make sure no actions are returned.
    assert len(context["available_actions"]) == 0


def test_get_context_builders():
    context_builders = get_context_builders()
    assert isinstance(context_builders, list)
    # Make sure there is at least one context builder.
    assert len(context_builders) > 0
