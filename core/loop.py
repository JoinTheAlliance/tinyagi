import memory

chroma_client = memory.get_client()
collections = memory.get_collections()


def compose_loop_prompt_template(task_id=None):
    #if(task_id == None):
        # handle standard loop prompt
        # LOOP -- time, date, goals, event stream
        

    #else:
        # handle task prompt

        # if task, build task prompt

        # if no task, build loop prompt


    # TASK -- time, date, event stream, task, task progress, other tasks

    # get the current user input

    # get self

    # get the current feed of memory

    # get the functions and inject them

    # prompt list of response actions

    loop_prompt_template = """\
The current time is {formatted_time} on {current_date}.
 
    """
    return loop_prompt_template


def main():
    print("Looping")
    # where = {
    #     "$and": [
    #         {"canceled": False},
    #         {"completed": False},
    #     ]
    # }

    # tasks = task_collection.get(where=where)

    # if len(tasks["ids"]) > 0:
    #     task_id = tasks["ids"][0]
    #     compose_loop_prompt_template(task_id=task_id)
    # else:
    #     compose_loop_prompt_template()
