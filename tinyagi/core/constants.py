import os
import dotenv

dotenv.load_dotenv()

DEBUG = os.environ.get("TINYAGI_DEBUG") in ["1", "true", "True"]

SIMILARY_THRESHOLD = 0.92 # used for cases of detecting if two things are the same, example knowledge matching
MAX_PROMPT_LIST_ITEMS = 30 # maximum number of 
MAX_PROMPT_LIST_TOKENS = 1536 # 2048 - 512
MAX_PROMPT_TOKENS = 3072 # 4096 - 1024
MAX_PROMPT_LIMIT = 15360 # 16384 - 1024