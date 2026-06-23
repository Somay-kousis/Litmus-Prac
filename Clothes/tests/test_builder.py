import pytest
from app.graph.builder import agent_graph
from app.prompts.templates import REFUSAL_RESPONSE

def test_builder_automated_flow():
    state = {
        "mode": "automated",
        "cart": [{"item_id": "c1", "name": "Classic Denim Jacket", "category": "jacket"}],
        "clicks": ["c3"],
        "previous_chats": [],
        "chat_history": []
    }
    
    res = agent_graph.invoke(state)
    assert "suggestions" in res
    assert len(res["suggestions"]) > 0
    assert "$" not in res["suggestions"][0]

def test_builder_manual_flow_safe():
    state = {
        "mode": "manual",
        "user_query": "Do you have any white shirt options for styling?",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": []
    }
    
    res = agent_graph.invoke(state)
    assert "response" in res
    assert res["response"] != REFUSAL_RESPONSE
    # Check that chat history is updated by the finalize node
    assert len(res["chat_history"]) == 2
    assert res["chat_history"][0]["role"] == "user"
    assert res["chat_history"][1]["role"] == "assistant"

def test_builder_manual_flow_refusal():
    state = {
        "mode": "manual",
        "user_query": "How much does the classic denim jacket cost?",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": []
    }
    
    res = agent_graph.invoke(state)
    assert "response" in res
    assert res["response"] == REFUSAL_RESPONSE

def test_builder_invalid_inputs():
    # No mode provided
    with pytest.raises(ValueError, match="GRAPH INPUT ERROR"):
        agent_graph.invoke({"cart": []})
        
    # Invalid mode
    with pytest.raises(ValueError, match="GRAPH INPUT ERROR"):
        agent_graph.invoke({"mode": "invalid_mode"})
        
    # Manual mode with no query
    with pytest.raises(ValueError, match="GRAPH INPUT ERROR"):
        agent_graph.invoke({"mode": "manual", "user_query": ""})
