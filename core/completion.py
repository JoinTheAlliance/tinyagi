import os
import openai
from dotenv import load_dotenv
import tiktoken
from core.memory import add_event
from datetime import datetime

from core.constants import (
    default_text_model,
    long_text_model,
    openai_api_key,
    default_max_tokens,
    agent_name,
)

load_dotenv()  # take environment variables from .env.

# Configure OpenAI API
openai.api_key = openai_api_key


def create_chat_completion(messages, functions=None, long=False):
    if long:
        model = long_text_model
    else:
        model = default_text_model
    # messages = trim_messages(messages, default_max_tokens)
    # if
    if functions == None or len(functions) == 0:
        response = openai.ChatCompletion.create(model=model, messages=messages)
    else:
        response = openai.ChatCompletion.create(
            model=model, messages=messages, functions=functions
        )

    # serialize the model, functions, messages and response to a text file and write it to logs/completions/<timestamp>.txt
    text = f"*** MODEL: {model}\n*** FUNCTIONS: {functions}\n*** MESSAGES: {messages}\n*** RESPONSE: {response}"

    # write the text to a file
    os.makedirs("logs/completions", exist_ok=True)

    # create a timestamp
    now = datetime.now()

    with open("logs/completions/" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".txt", "w") as f:
        f.write(text)

    response_data = response["choices"][0]["message"]

    message = response_data["content"]

    # check if response_data["function_call"] exists
    if "function_call" in response_data:
        function_call = response_data["function_call"]
        return {"message": message, "function_call": function_call}
    else:
        return {"message": message, "function_call": None}


encoding = tiktoken.encoding_for_model(default_text_model)

def trim_messages(messages, max_tokens):
    new_messages = []

    tokens_per_message = 3
    tokens_per_name = 1
    original_num_tokens = count_tokens_from_chat_messages(messages)

    if(original_num_tokens <= max_tokens):
        return messages

    num_tokens = 0
    break_outer = False  # flag to break outer loop from within inner one

    for message in messages:
        if break_outer:
            break

        num_tokens_temp = num_tokens + tokens_per_message
        for key, value in message.items():
            if key == "name":
                num_tokens_temp += tokens_per_name
            else:
                num_tokens_temp += len(encoding.encode(value))

            if num_tokens_temp > max_tokens:
                break_outer = True  # set flag to break outer loop
                break

        if not break_outer:  # only append the message if it doesn't exceed the max tokens
            new_messages.append(message)
            num_tokens = num_tokens_temp  # update the number of tokens after the message is appended

    # ensure the last message of messages is included
    if len(new_messages) == 0:
        message = messages[-1]

        # get number of tokens in the message
        new_num_tokens = count_tokens_from_chat_messages([message])

        # if the message is too long, trim it
        if new_num_tokens > max_tokens:
            # remove tokens from the top of the message until it's short enough
            while new_num_tokens > max_tokens:
                # remove the first 100 tokens from the message
                message["content"] = message["content"][10:]
                # explain how the [100:] works
                # https://stackoverflow.com/questions/509211/understanding-slice-notation

                new_num_tokens = count_tokens_from_chat_messages([message])

        new_messages.append(message)
    if original_num_tokens != num_tokens:
        add_event(
            "I trimmed some messages to make them fit in my memory. The original number was "
            + str(original_num_tokens)
            + " and the new number is "
            + str(num_tokens),
            agent_name,
            "completion_status",
        )
    return new_messages

def count_tokens_from_chat_messages(messages):
    tokens_per_message = 3
    tokens_per_name = 1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    return num_tokens


def count_tokens(text):
    return len(encoding.encode(text))
