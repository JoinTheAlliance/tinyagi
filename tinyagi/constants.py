MAX_PROMPT_LIST_ITEMS = 30  # maximum number of events to display
MAX_PROMPT_LIST_TOKENS = 1536  # 2048 - 512
MAX_PROMPT_TOKENS = 3072  # 4096 - 1024

loop_dict = None
def set_loop_dict(new_dict):
    global loop_dict
    loop_dict = new_dict

def get_loop_dict():
    global loop_dict
    return loop_dict