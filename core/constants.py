import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
agent_name = os.getenv("AGENT_NAME")

update_interval = int(os.getenv("UPDATE_INTERVAL"))

default_text_model = os.getenv("DEFAULT_TEXT_MODEL")
long_text_model = os.getenv("LONG_TEXT_MODEL")
default_max_tokens = int(os.getenv("DEFAULT_MAX_TOKENS"))

# Configure OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")