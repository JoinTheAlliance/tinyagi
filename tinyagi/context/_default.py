import os
import sys
from datetime import datetime

from agentevents import (
    get_epoch,
)


def compose_default_context(context=None):
    """
    Create a default context object

    Args:
        context: the last context made by the loop. Defaults to None.

    Returns:
        context: a dictionary containing the current context
    """
    context = {
        "current_time": datetime.now().strftime("%H:%M"),
        "current_date": datetime.now().strftime("%Y-%m-%d"),
        "platform": sys.platform,
        "cwd": os.getcwd(),
    }

    return context
