import time
import os

from core.skill_handling import register_skills

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
    time.sleep(5)
    print("looping")
    core.loop.main()