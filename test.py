import os
from dotenv import load_dotenv
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "False"

from tests.system import run_tests as run_system_tests
from tests.events import run_tests as run_event_tests
from tests.knowledge import run_tests as run_knowledge_tests
from tests.actions import run_tests as run_action_tests
from tests.loop import run_tests as run_loop_tests
from agentmemory import wipe_all_memories
if __name__ == "__main__":
    # Initialize the agent
    wipe_all_memories()
    run_loop_tests()
    run_system_tests()
    run_action_tests()
    run_knowledge_tests()
    run_event_tests()
    print("All tests passed!")
