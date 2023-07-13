"""
easycompletion

Leveraging conversational AI for bicameral decision making.
"""

__version__ = "0.1.8"
__author__ = "Moon (https://github.com/lalalune)"
__credits__ = "https://github.com/lalalune/tinyagi"

from .core.actions import (
    add_to_action_history,
    get_action_history,
    get_last_action,
    get_available_actions,
    search_actions,
    use_action,
    add_action,
    get_action,
    remove_action,
    register_actions,
)

from .core.events import (
    get_event_epoch,
    increment_event_epoch,
    write_to_log,
    create_event,
    get_events,
    search_events,
)

from .core.knowledge import (
    add_new_knowledge,
    create_knowledge,
    remove_knowledge,
    delete_knowledge_by_id,
    search_knowledge,
)


from .core.loop import start, loop


__all__ = [
    "add_to_action_history",
    "get_action_history",
    "get_last_action",
    "get_available_actions",
    "search_actions",
    "use_action",
    "add_action",
    "get_action",
    "remove_action",
    "register_actions",
    "get_event_epoch",
    "increment_event_epoch",
    "write_to_log",
    "create_event",
    "get_events",
    "search_events",
    "add_new_knowledge",
    "create_knowledge",
    "remove_knowledge",
    "delete_knowledge_by_id",
    "search_knowledge",
    "start",
    "loop",
]
