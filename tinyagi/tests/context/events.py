from tinyagi.context.events import (
    event_to_string,
    build_events_context,
    get_context_builders,
)


def test_event_to_string():
    event = {
        "metadata": {
            "epoch": None,
            "type": None,
            "subtype": "subtype1",
            "creator": "creator1",
        },
        "document": "document1",
    }
    expected_output = "0 | unknown::subtype1 (creator1): document1"
    assert event_to_string(event) == expected_output


def test_build_events_context():
    context = {}
    context = build_events_context(context)

    assert "events" in context
    assert context["events"].startswith("Recent Events are formatted as follows")
    assert "0 | unknown: document" in context["events"]


def test_get_context_builders():
    builders = get_context_builders()
    assert len(builders) == 1
    assert builders[0].__name__ == "build_events_context"
