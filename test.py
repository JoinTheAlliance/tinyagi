from tests.events import run_tests as run_event_tests
from tests.knowledge import run_tests as run_knowledge_tests
from tests.actions import run_tests as run_action_tests
from agentmemory import wipe_all_memories

# Initialize the agent
wipe_all_memories()

run_action_tests()

run_knowledge_tests()

run_event_tests()