# plan about things that are going on
from core.language import use_language_model, compose_prompt
from core.memory import add_event, get_all_values_for_text, get_documents
from core.constants import agent_name


def get_skills():
    return {
        "form_plan": {
            "payload": {
                "name": "form_plan",
                "description": "Form a plan for what you're going to do to achieve your goals or tasks. Good when you're just getting started.",
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
        add_event(
            f"(plan) My most recent plan is this one: \n{document}",
            agent_name,
            type="plan",
        )
    else:
        add_event(f"(plan) I don't have a plan.", agent_name, type="plan")


def plan(arguments):
    plan = arguments.get("plan", None)
    values_to_replace = get_all_values_for_text(plan)
    user_prompt = compose_prompt("plan", values_to_replace)
    system_prompt = compose_prompt("system", values_to_replace)

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]
    response = use_language_model(messages=messages)
    response_message = response.get("message", None)
    if response_message != None:
        response_message = "(planning) " + response_message
        add_event(response_message, agent_name, type="plan")


if __name__ == "__main__":
    # Test `plan` function
    try:
        plan({"plan": "My plan is to test the function"})
    except Exception as e:
        print(f"The `plan` function failed with exception: {e}")

    # Test `remember_plan` function
    try:
        remember_plan(None)
        print("The `remember_plan` function ran successfully")
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
