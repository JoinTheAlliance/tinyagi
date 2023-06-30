import openai
from utils import write_debug_log
from constants import default_text_model, openai_api_key, default_max_tokens
from dotenv import load_dotenv
import time

load_dotenv()  # take environment variables from .env.

# Configure OpenAI API
openai.api_key = openai_api_key


def create_chat_completion(messages, functions=None, model=default_text_model):
    messages = trim_messages(messages, default_max_tokens)
    # if
    if functions == None:
        response = openai.ChatCompletion.create(model=model, messages=messages)
    else:
        response = openai.ChatCompletion.create(
            model=model, messages=messages, functions=functions
        )

    response_str = str(response)

    response_data = response["choices"][0]["message"]

    message = response_data["content"]

    function = response_data.get("function", None)

    write_debug_log("create_chat_completion called")
    write_debug_log("messages: " + str(messages))
    write_debug_log("functions: " + str(functions))
    write_debug_log("response_str: " + response_str)

    return {"message": message, "function": function}

import tiktoken

encoding = tiktoken.encoding_for_model(default_text_model)

def trim_messages(messages, max_tokens):
    # remove any messages except for the last user message until the total number of tokens is less than max_tokens
    # if the last message is a user message, remove text from the top of the message
    new_messages = []

    tokens_per_message = 3
    tokens_per_name = 1
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
            if num_tokens > max_tokens:
                break
            else:
                new_messages.append(message)
    
    # make sure that the last message of messages is definitely included
    if len(new_messages) == 0:
        message = messages[-1]

        # get the number of tokens in the message
        num_tokens = count_tokens_from_chat_messages([message])

        # if the message is too long, trim it
        if num_tokens > max_tokens:
            # remove tokens from the top of the message until the message is short enough
            while num_tokens > max_tokens:
                # remove the first 100 tokens from the message
                message["content"] = message["content"][100:]
                num_tokens = count_tokens_from_chat_messages([message])
            new_messages.append(message)

        new_messages.append(message)
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
