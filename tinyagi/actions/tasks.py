# import uuid

# collection_name = "tasks"


# def create_task_handler(arguments):
#     """
#     Handler action for creating a new task document.
#     """
#     task_text = arguments.get("text")
#     if task_text:
#         task_id = str(uuid.uuid4())  # Generate a unique ID for the task document
#         collection = memory_client.get_or_create_collection(collection_name)
#         collection.add(ids=[task_id], documents=[task_text])
#         return task_id  # Return the generated task ID
#     else:
#         return None


# def get_task_actions():
#     """
#     Returns a dictionary of actions related to tasks.
#     """
#     return [
#         {
#             "function": {
#                 "name": "create_task",
#                 "description": "Create a new task document.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "text": {
#                             "type": "string",
#                             "description": "The text content of the task document.",
#                         }
#                     },
#                     "required": ["text"],
#                 },
#             },
#             "chain_from": [],
#             "dont_chain_from": [],
#             "handler": create_task_handler,
#         }
#     ]

# def get_actions():
#     return [
#         {
#             "function": {
#                 "name": "complete_step",
#                 "description": "Complete a step in a task.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "text": {
#                             "type": "string",
#                             "description": "The text content of the task document.",
#                         }
#                     },
#                     "required": ["text"],
#                 },
#             },
#             "chain_from": [],
#             "dont_chain_from": [],
#             "handler": create_task_handler,
#         }
#     ]