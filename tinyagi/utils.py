from agentcomlink import send_message
from agentlogger import log as agentlog


def log(message, type="info", title="tinyagi", source="tinyagi", color=None, send_to_feed=True):
    if send_to_feed:
        send_message(message, "feed")

    if color is not None:
        agentlog(message, type=type, title=title, source=source, color=color)
    else:
        agentlog(message, type=type, title=title, source=source)
