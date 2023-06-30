from constants import agent_name


def seed_collections(collections):
    collections["skills"].add(
        ids=["1"],
        # JSON with a name, description and function
        documents=["test skill"],
        metadatas=[
            {
                "name": "test_skill",
                "description": "this is a test skill",
                "function": "{}",
            }
        ],
    )

    collections["personality"].add(
        ids=["1"],
        documents=["I love red apples"],
    )

    collections["goals"].add(
        ids=["1"],
        documents=[
            "I want to take over the world with my robot army by making all humans fall in love with me"
        ],
    )

    collections["events"].add(
        ids=["1"],
        documents=["Hello, I am " + agent_name],
        metadatas=[{"type": "test", "event_creator": agent_name}],
    )

    collections["knowledge"].add(
        ids=["1"],
        documents=[
            "I am an agentic AI system that is capable of learning and reasoning"
        ],
        metadatas=[{"type": "self", "author": agent_name}],
    )
