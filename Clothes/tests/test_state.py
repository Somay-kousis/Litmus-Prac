import pytest
from app.graph.reducers import merge_lists, merge_messages, merge_dict
from app.graph.state import AssistantState

def test_merge_lists():
    # Test merging lists with duplicate removal
    list1 = ["item1", "item2"]
    list2 = ["item2", "item3"]
    result = merge_lists(list1, list2)
    assert result == ["item1", "item2", "item3"]

    # Test with empty inputs
    assert merge_lists(None, ["a"]) == ["a"]
    assert merge_lists(["b"], None) == ["b"]

def test_merge_messages():
    # Test replacing message lists (supports parenthetical truncation)
    msg1 = [{"role": "user", "content": "hello"}]
    msg2 = [{"role": "assistant", "content": "hi"}]
    result = merge_messages(msg1, msg2)
    assert len(result) == 1
    assert result[0]["content"] == "hi"

def test_merge_dict():
    # Test merging dictionaries of profiles
    dict1 = {"brother": {"size": "L", "style": "casual"}}
    dict2 = {"brother": {"style": "streetwear", "color": "black"}, "mom": {"size": "S"}}
    result = merge_dict(dict1, dict2)
    
    assert result["brother"]["size"] == "L"
    assert result["brother"]["style"] == "streetwear"
    assert result["brother"]["color"] == "black"
    assert result["mom"]["size"] == "S"

def test_state_structure():
    # Test state fields validation structure
    state: AssistantState = {
        "cart": [{"item_id": "1", "name": "Shirt", "category": "shirt", "color": "blue", "size": "M"}],
        "clicks": ["jacket_1", "shoes_2"],
        "previous_chats": ["Asked for sizing earlier"],
        "chat_history": [{"role": "user", "content": "Help me pick a jacket"}],
        "recipient": "brother",
        "recipient_profiles": {"brother": {"size": "L"}},
        "suggestions": ["Blue Jacket matching with shirt"],
        "response": "Here is my advice..."
    }
    assert len(state["cart"]) == 1
    assert state["cart"][0]["name"] == "Shirt"
    assert state["recipient"] == "brother"
    assert state["recipient_profiles"]["brother"]["size"] == "L"
    assert "price" not in state["cart"][0]  # Guardrail check: no price in initial model definition
