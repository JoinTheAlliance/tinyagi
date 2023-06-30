import openai
from utils import debug_write_file
from constants import default_text_model, openai_api_key
from dotenv import load_dotenv
import time
load_dotenv()  # take environment variables from .env.

# Configure OpenAI API
openai.api_key = openai_api_key

def create_chat_completion(messages, functions=None, model=default_text_model):
    # if
    if functions == None:
      response = openai.ChatCompletion.create(
        model=model,
        messages=messages
      )
    else:
      response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions
      )

    response_str = str(response)

    response_data = response["choices"][0]["message"]

    message = response_data["content"]

    function = response_data.get("function", None)

    debug_write_file(response_str, "responses/response_"+str(time.time()))

    return {
        "message": message,
        "function": function
    }