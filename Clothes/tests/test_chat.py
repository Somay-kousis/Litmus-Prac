import pytest
from app.nodes.chat_assistant import chat_assistant, is_pricing_query
from app.prompts.templates import REFUSAL_RESPONSE
from app.graph.state import AssistantState

def test_is_pricing_query():
    assert is_pricing_query("How much does this cost?") is True
    assert is_pricing_query("Is there a discount code?") is True
    assert is_pricing_query("What is the price of the jacket?") is True
    assert is_pricing_query("Does this jacket match with these boots?") is False
    assert is_pricing_query("Do you have size medium?") is False

def test_chat_first_message_greeting():
    # If first message is a general greeting, assistant asks who they are shopping for
    state: AssistantState = {
        "user_query": "hello",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": []
    }
    result = chat_assistant(state)
    assert result["response"] == "Hey, who are we looking for clothes for today?"
    assert result["recipient"] == "self"

def test_chat_recipient_someone_else_new():
    # User says shopping for someone else/brother, assistant asks for details
    state: AssistantState = {
        "user_query": "I am looking for clothes for my brother today",
        "cart": [{"item_id": "c3", "name": "White Linen Shirt", "category": "shirt"}],
        "clicks": [],
        "previous_chats": [],
        "chat_history": [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "Hey, who are we looking for clothes for today?"}],
        "recipient_profiles": {}
    }
    result = chat_assistant(state)
    assert "brother" in result["recipient"]
    assert "cart won't be used" in result["response"] or "ignore your current cart" in result["response"]
    assert "style preference" in result["response"] or "size" in result["response"]

def test_chat_recipient_memory_lookup():
    # User says shopping for brother, profile is in memory, assistant acknowledges
    state: AssistantState = {
        "user_query": "I am looking for my brother",
        "cart": [{"item_id": "c3", "name": "White Linen Shirt", "category": "shirt"}],
        "clicks": [],
        "previous_chats": [],
        "chat_history": [],
        "recipient": "self",
        "recipient_profiles": {
            "brother": {"preferences": "Size L and loves streetwear"}
        }
    }
    result = chat_assistant(state)
    assert result["recipient"] == "brother"
    assert "Size L and loves streetwear" in result["response"]
    assert "ignore" in result["response"] or "won't be used" in result["response"]

def test_chat_save_recipient_preferences():
    # User provides preferences for brother, verify they are extracted and saved
    state: AssistantState = {
        "user_query": "He is size M and likes minimalist grey items",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": [
            {"role": "user", "content": "buying for my brother"},
            {"role": "assistant", "content": "Got it! Tell me his style preferences."}
        ],
        "recipient": "brother",
        "recipient_profiles": {
            "brother": {}
        }
    }
    result = chat_assistant(state)
    assert result["recipient"] == "brother"
    prefs = result["recipient_profiles"]["brother"]["preferences"]
    assert "size M" in prefs.lower() or "minimalist" in prefs.lower() or "grey" in prefs.lower()

def test_chat_assistant_pricing_query():
    state: AssistantState = {
        "user_query": "Can you give me a coupon code or a discount on the white shirt?",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": []
    }
    result = chat_assistant(state)
    assert result["response"] == REFUSAL_RESPONSE

def test_chat_assistant_invalid_input():
    state: AssistantState = {
        "user_query": "",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": []
    }
    with pytest.raises(ValueError, match="INPUT STATE ERROR"):
        chat_assistant(state)

def test_chat_wardrobe_contrast():
    # User asks to buy/suggest a grey jacket, but they already own it in db
    from app.data.db_store import db_store
    db_store.clear()
    
    state: AssistantState = {
        "user_query": "How about getting a grey jacket?",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": [],
        "recipient": "self",
        "recipient_profiles": {}
    }
    
    result = chat_assistant(state)
    response_text = result["response"]
    # Check that stylist warns they already have a grey jacket and suggests alternative to make wardrobe complement
    assert "already have" in response_text.lower() or "already own" in response_text.lower()
    assert "wardrobe" in response_text.lower()

def test_chat_extract_wardrobe_goals_occupation():
    # User mentions occupation, items owned, and shopping goals in chat query
    from app.data.db_store import db_store
    db_store.clear()

    state: AssistantState = {
        "user_query": "I am a designer and I already have a blue sweater in my wardrobe. I need to buy 3 clothing items today.",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": [],
        "recipient": "self",
        "recipient_profiles": {}
    }
    
    result = chat_assistant(state)
    
    # Verify values are correctly parsed and saved to local DB
    profile = db_store.get_profile("self")
    assert profile["occupation"] == "designer"
    assert "blue sweater" in profile["wardrobe"]
    assert profile["shopping_goals"]["pieces_needed"] == 3
