import os
import sys
from datetime import datetime


def compose_default_context(context={}):
    """
    Create a default context object

    Args:
        context: the last context made by the loop. Defaults to None.

    Returns:
        context: a dictionary containing the current context
    """
    context["current_time"] = datetime.now().strftime("%H:%M")
    context["current_date"] = datetime.now().strftime("%Y-%m-%d")
    context["platform"] = sys.platform
    context["cwd"] = os.getcwd()
    return context

def get_context_builders():
    """
    Returns a list of functions that build context dictionaries

    Returns:
        context_builders: a list of functions that build context dictionaries
    """
    return [compose_default_context]