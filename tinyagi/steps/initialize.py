import datetime
import os
import sys
from agentmemory import get_epoch

from agentmemory import set_epoch

from tinyagi.utils import log

from datetime import datetime


def initialize(context={}):
    """
    Initialize the loop with context

    Args:
        context: the last context made by the loop. Defaults to None.

    Returns:
        context: a dictionary containing the current context
    """
    set_epoch(get_epoch() + 1)
    if context is None:
        context = {}
        context["epoch"] = get_epoch()
        context["last_epoch"] = 0
    else:
        context["last_epoch"] = context.get("epoch", 0)
        context["epoch"] = get_epoch()
    context["current_time"] = datetime.now().strftime("%H:%M")
    context["current_date"] = datetime.now().strftime("%Y-%m-%d")
    context["platform"] = sys.platform
    context["cwd"] = os.getcwd()

    context["verbose"]="--verbose" in os.sys.argv



    log(
        "Start for epoch "
        + str(context["epoch"])
        + " at "
        + str(context["current_time"]),
        type="step",
        source="initialize",
        title="tinyagi",
        send_to_feed=False,
    )

    return context
