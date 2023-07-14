"""
tinyagi

A really simple approach to a self-learning, open-ended system.
"""

__version__ = "0.1.0"
__author__ = "Autonomous Research Group"
__credits__ = "https://github.com/AutonomousResarchGroup/tinyagi"

from .core.system import (
    get_epoch,
    increment_epoch,
)

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
    get_actions,
)

from .core.events import (
    write_to_log,
    create_event,
    get_events,
    search_events,
)

from .core.knowledge import (
    add_knowledge,
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
    "get_actions",
    "get_epoch",
    "increment_epoch",
    "write_to_log",
    "create_event",
    "get_events",
    "search_events",
    "add_knowledge",
    "remove_knowledge",
    "delete_knowledge_by_id",
    "search_knowledge",
    "start",
    "loop",
]
