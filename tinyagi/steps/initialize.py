import datetime
import os
import sys

from agentlogger import log

from datetime import datetime

def initialize(context={}):
    """
    Initialize the loop with context

    Args:
        context: the last context made by the loop. Defaults to None.

    Returns:
        context: a dictionary containing the current context
    """
    if context is None:
        context = {}
        context["epoch"] = 0
    else:
        context["epoch"] = context.get("epoch", 0) + 1
    context["current_time"] = datetime.now().strftime("%H:%M")
    context["current_date"] = datetime.now().strftime("%Y-%m-%d")
    context["platform"] = sys.platform
    context["cwd"] = os.getcwd()

    log("Start for epoch " + str(context["epoch"]) + " at " + str(context["current_time"]), type="step", source="initialize", title="tinyagi")

    return context
