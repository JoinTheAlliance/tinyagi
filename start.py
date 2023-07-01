import time
import os

from core.skills import register_skills
from core.constants import update_interval

import core.loop
import core.memory

chroma_client = core.memory.get_client()
collections = core.memory.get_collections()

# delete logs folder
os.system("rm -rf logs")

# regenerate codebase log
os.system("python3 scripts/generate_code.py")

register_skills()

while True:
    time.sleep(update_interval)
    core.loop.main()
