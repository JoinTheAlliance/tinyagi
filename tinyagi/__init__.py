"""
tinyagi

A really simple approach to a self-learning, open-ended system.
"""

__version__ = "0.1.0"
__author__ = "Autonomous Research Group"
__credits__ = "https://github.com/AutonomousResarchGroup/tinyagi"

from .core.knowledge import (
    add_knowledge,
    remove_knowledge,
    delete_knowledge_by_id,
    search_knowledge,
)


__all__ = [
    "add_knowledge",
    "remove_knowledge",
    "delete_knowledge_by_id",
    "search_knowledge",
]
