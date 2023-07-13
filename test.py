from tests.events import run_tests as run_event_tests
from agentmemory import wipe_all_memories

# Initialize the agent
wipe_all_memories()

run_event_tests()