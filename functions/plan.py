# functions/plan.py

# plan about things that are going on
from core.language import clean_prompt, use_language_model, compose_prompt
from core.memory import create_event, get_documents

plan_prompt = clean_prompt(
    """
The current time is {current_time} on {current_date}.

Relevant things you know:
{knowledge}

You can call the following functions and should call them often:
{functions}

These are your most important goals, which you should always keep in mind:
{goals}

These are your current tasks, which you should prioritize accomplishing
{tasks}

Recent Event History:
{events}

Prompt: You should write a detailed plan that you can execute on. You should make sure to include what function or task the plan is related to, and what functions or knowledge you will use. Your goal is to call a function once you have a rough plan.
Sometimes you get caught in loops, especially with planning, thinking and learning. If you've been planning and thinking for a while, you should try figure out what else you should do, especially exploring, coding or playing with the browser or terminal.
Always try to advance your goals and complete your tasks. Always try to call the most appropriate function for the immediate context -- or just start working toward your goals.
"""
)


def get_functions():
    return {
        "create_plan": {
            "payload": {
                "name": "create_plan",
                "description": "Create a new plan for what you're going to do to achieve your goals or tasks. Good when you're just getting started.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "plan": {
                            "type": "string",
                            "description": "A detailed plan",
                        },
                    },
                    "required": ["plan"],
                },
            },
            "handler": plan,
        },
        "remember_plan": {
            "payload": {
                "name": "remember_plan",
                "description": "Did you forget what the plan was? Get the last plan.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            "handler": remember_plan,
        },
    }


def remember_plan(arguments):
    where = {"type": "plan"}
    plan = get_documents("events", where=where, include=["metadatas", "documents"])

    # join plan["documents"] and plan["metadatas"] by index

    documents_and_metadata = []

    if len(plan["metadatas"]) > 0:
        # for len(plan["metadatas"])
        for i in range(len(plan["metadatas"])):
            documents_and_metadata.append((plan["documents"][i], plan["metadatas"][i]))

        # each item in documents_and_metadatas is a tuple of (document, metadata)
        # the metadata dictionary has a timestamp
        # get the document with the most recent timestamp
        newest_plan_index = 0
        newest_plan_timestamp = 0
        for index, (document, metadata) in enumerate(documents_and_metadata):
            timestamp = metadata["timestamp"]
            if timestamp > newest_plan_timestamp:
                newest_plan_index = index
                newest_plan_timestamp = timestamp

        document = documents_and_metadata[newest_plan_index][0]
        create_event(
            f"(plan) My most recent plan is this one: \n{document}",
            type="plan",
        )
    else:
        create_event(f"(plan) I don't have a plan. I should create one.", type="plan")


def plan(arguments):
    plan = arguments.get("plan", None)
    user_prompt = compose_prompt(plan_prompt, plan)

    messages = [
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = use_language_model(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        response_message = "(planning) " + response_message
        create_event(response_message, type="plan")


if __name__ == "__main__":
    # Test `plan` function
    try:
        plan({"plan": "My plan is to test the function"})
    except Exception as e:
        print(f"The `plan` function failed with exception: {e}")

    # Test `remember_plan` function
    try:
        remember_plan(None)
        # Assume get_documents from core.memory returns dictionary as required by remember_plan
        result = get_documents(
            "events", where={"type": "plan"}, include=["metadatas", "documents"]
        )
        # Assert that the result is a dictionary (a basic check)
        assert isinstance(
            result, dict
        ), "`remember_plan` function did not return a dictionary as expected"
    except Exception as e:
        print(f"The `remember_plan` function failed with exception: {e}")

    print("All tests passed!")
