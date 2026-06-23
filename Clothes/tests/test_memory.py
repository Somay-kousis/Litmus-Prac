import pytest
from app.graph.builder import agent_graph

def test_sliding_window_compression():
    # Construct a chat history with 50 messages (25 user, 25 assistant)
    chat_history = []
    for i in range(25):
        chat_history.append({"role": "user", "content": f"User msg {i+1}"})
        chat_history.append({"role": "assistant", "content": f"Assistant response {i+1}"})

    # Assert history length is 50 before sending the new query
    assert len(chat_history) == 50

    # Sending 51st message (which triggers builder finalize_response compression)
    state = {
        "mode": "manual",
        "user_query": "What jacket goes well with black tee?",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": chat_history,
        "recipient": "self",
        "recipient_profiles": {},
        "summary": None
    }

    res = agent_graph.invoke(state)

    # The resulting history must be capped to exactly 50 messages
    # (Since 50 + 2 new messages were combined, 2 oldest messages must be popped)
    assert len(res["chat_history"]) == 50
    assert res["summary"] is not None

    # The oldest popped messages should be User msg 1 and Assistant response 1
    # Verify summary structure matches: ( [USER]: User msg 1 + [ASSISTANT]: Assistant response 1 )
    assert "[USER]: User msg 1" in res["summary"]
    assert "[ASSISTANT]: Assistant response 1" in res["summary"]
    assert res["summary"].startswith("([USER]: User msg 1 +") or res["summary"].startswith("(")
