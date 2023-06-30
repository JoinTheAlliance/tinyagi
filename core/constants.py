import os
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
agent_name = os.getenv("AGENT_NAME")

default_text_model = os.getenv("DEFAULT_TEXT_MODEL")

# Configure OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")

collection_names = [
    "user_events",
    "people",
    "skills",
    "goals",
    "events",
    "tasks"
]

debug = os.getenv("DEBUG") == "True" or os.getenv("DEBUG") == "true"
respond_to_user_input = os.getenv("RESPOND_TO_USER_INPUT") == "True" or os.getenv("RESPOND_TO_USER_INPUT") == "true"