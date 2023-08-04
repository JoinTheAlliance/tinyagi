from agentcomlink import send_message
from agentlogger import log as agentlog, DEFAULT_TYPE_COLORS


def log(message, header=None, type="info", title="tinyagi", source="tinyagi", color=None, send_to_feed=True):
    if send_to_feed:
        if color is None:
            send_color = DEFAULT_TYPE_COLORS.get(type, "white")
        else:
            send_color = color

        # if message is not a str
        if not isinstance(message, str) and message.get("message", None) is not None:
            message = message["message"]
        elif not isinstance(message, str):
            message = str(message)

        output = {
            "message": message,
            "header": header,
            "color": send_color,
        }
        send_message(output, "feed", "log")

        print('**********')
        print('message', message)
        print('header', header)
        print('type', type)

    # if header is a dict
    if isinstance(header, dict):
        header = header.get("message", str(header))

    message_out = f"# {header}\n" + message if header else message

    if color is not None:
        agentlog(message_out, type=type, title=title, source=source, color=color, panel=False)
    else:
        agentlog(message_out, type=type, title=title, source=source, panel=False)
