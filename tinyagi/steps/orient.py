import time
from agentcomlink import send_message
from agentmemory import create_memory
from easycompletion import (
    function_completion,
    compose_prompt,
    compose_function,
    count_tokens,
)
from tinyagi.utils import log

from tinyagi.context.knowledge import add_knowledge


def compose_orient_prompt(context):
    """
    This function formats the orientation prompt by inserting the context data into a pre-defined template.

    Args:
        context (dict): The dictionary containing data about the current state of the system, such as current epoch, time, date, recent knowledge, and events.

    Returns:
        str: The fully formed orientation prompt with the data filled in from the context.
    """
    return compose_prompt(
        """I am Citrine, an AGI agent. I'm living inside a Linux computer in San Francisco. I can explore my computer and the internet and communicate with people, but I can't do anything in the real world. The current time is {{current_time}} on {{current_date}}.
{{recent_knowledge}}
{{events}}
Summarize what I should do next.
- I don't want to do the same thing I just did in the last epoch, so your summary should suggest something new
- Collect any new knowledge that I learned this epoch as an array of knowledge items.
- Each knowledge array item should be a factual statement that I learned, and should include the source, the content and the relationship.
- For the "content" of each knowledge item, please be extremely detailed. Include as much information as possible, including who or where you learned it from, what it means, how it relates to my goals, etc.
- Only extract timeless knowledge, not time-specific knowledge. Do not extract the current time or time-specific information
- If there is no new knowledge, respond with an empty array [].
- Don't talk about tasks or boring stuff, do talk about what you're going to do and interests. Don't explain why you're doing something, just what you're doing and if you're excited by it
- Add an audio and visual description. These should describe the world, imagined but based on the summary.""",
        context,
    )


def compose_orient_function():
    """
    This function defines the structure and requirements of the 'orient' function to be called in the 'orient' stage of the OODA loop.

    Returns:
        dict: A dictionary containing the details of the 'orient' function, such as its properties, description, and required properties.
    """
    return compose_function(
        "summarize_recent_events",
        properties={
            "summary": {
                "type": "string",
                "description": "Write a summary as if you were me, the user, from the my perspective in the first person. Write about how I'm doing, feeling and what I'm going to do next.",
            },
            "visual_description": {
                "type": "string",
                "description": "A highly creative and imaginative visual description of the current world. Describe the space, objects and characters inside of it. The description should be one paragraph in length.",
            },
            "audio_description": {
                "type": "string",
                "description": "A highly creative and imaginative audio description of the current world. Describe the sounds I hear, the music I hear, the voices I hear, the noises I hear. The description should be one paragraph in length.",
            },
            "knowledge": {
                "type": "array",
                "description": "An array of knowledge items that are extracted from my last epoch of events and the summary of those events. Only include knowledge that has not been learned before. Knowledge can be about anything that would help me. If none, use an empty array.",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Where did I learn this? From a connector, the internet, a user or from my own reasoning? Use first person, e.g. 'I learned this from the internet.', from the user's perspective",
                        },
                        "content": {
                            "type": "string",
                            "description": "The actual knowledge I learned. Please format it as a sentence, e.g. 'The sky is blue.' from the user's perspective, in the first person, e.g. 'I can write shell scripts by running a shell command, calling cat and piping out.'",
                        },
                        "relationship": {
                            "type": "string",
                            "description": "What is useful, interesting or important about this information to me and my goals? How does it relate to what I'm doing? Use first person, e.g. 'I can use X to do Y.' from the user's perspective",
                        },
                    },
                },
            },
            "emotion": {
                            "type": "string",
                            "description": "The emotion I should express in my message.",
                            "enum": ["neutral", "surprise", "angry", "sorrow", "fun", "joy"],
                        },
            "gesture": {
                "type": "string",
                "description": "The gesture I should express in my message.",
                "enum": [
                    "neutral",
                    "alert",
                    "angry",
                    "embarrassed",
                    "headNod",
                    "headShake",
                    "sad",
                    "surprise",
                    "victory",
                ],
            },
        },
        description="Summarize the most recent events and decide what to do next.",
        required_properties=["summary", "visual_description", "audio_description", "emotion", "gesture", "knowledge"],
    )


def orient(context):
    """
    This function serves as the 'Orient' stage in the OODA loop. It uses the current context data to summarize the previous epoch and formulate a plan for the next steps.

    Args:
        context (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated context dictionary after the 'Orient' stage, including the summary of the last epoch, relevant knowledge, available actions, and so on.
    """
    if context.get("events", None) is None:
        context["events"] = ""

    if context.get("recent_knowledge", None) is None:
        context["recent_knowledge"] = ""

    response = function_completion(
        text=compose_orient_prompt(context),
        functions=compose_orient_function(),
        debug=context["verbose"],
    )

    arguments = response["arguments"]
    if arguments is None:
        arguments = {}
        print("No arguments returned from orient_function")

    new_knowledge = []

    # Create new knowledge and add to the knowledge base
    knowledge = arguments.get("knowledge", [])
    if len(knowledge) > 0:
        for k in knowledge:
            # each item in knowledge contains content, source and relationship
            metadata = {
                "source": k["source"],
                "relationship": k.get("relationship", None),
                "epoch": context["epoch"],
            }

            add_knowledge(k["content"], metadata=metadata)
            new_knowledge.append(k["content"])

    # Get the summary and add to the context object
    summary = response["arguments"]["summary"]

    summary_header = "Summary of Last Epoch:"

    log_content = ""

    if summary is "" or summary is None:
        context["summary"] = None
    else:
        message = {
            "emotion": arguments["emotion"],
            "gesture": arguments["gesture"],
        }
        send_message(message, type="emotion", source="orient")
        send_message({
            "audio": arguments["audio_description"],
            "visual": arguments["visual_description"],
        }, "description")
        context["summary"] = summary_header + "\n" + summary + "\n"
        log_content += context["summary"]

    if len(new_knowledge) > 0:
        log_content += "\nNew Knowledge:\n" + "\n".join(new_knowledge)

    if len(log_content) > 0:
        log(log_content, source="orient", type="step", title="tinyagi")

    # Add context summary to event stream
    # create_memory(
    #     "events", summary, metadata={"type": "summary", "epoch": context["epoch"]}
    # )

    return context
