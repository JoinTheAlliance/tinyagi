import os
import shutil
# if .env doesn't exist, copy .env.example to .env
if not os.path.exists(".env"):
    shutil.copy(".env.example", ".env")
    print("Please edit the .env file and add your API key, then restart the agent")
    exit()

import time

from core.skills import register_skills
from core.constants import update_interval

import core.loop

register_skills()

while True:
    time.sleep(update_interval)
    core.loop.main()
