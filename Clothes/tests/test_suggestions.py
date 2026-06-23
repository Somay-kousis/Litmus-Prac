import pytest
from app.nodes.generate_daily_suggestions import generate_daily_suggestions, check_pricing_guardrails
from app.graph.state import AssistantState

def test_check_pricing_guardrails():
    # Should not raise any errors on normal style content
    check_pricing_guardrails("This is a beautiful blue denim jacket that matches beige pants.")
    
    # Should raise error on price symbols
    with pytest.raises(ValueError, match="GUARDRAIL VIOLATION"):
        check_pricing_guardrails("This jacket costs $50.")
        
    # Should raise error on discount keywords
    with pytest.raises(ValueError, match="GUARDRAIL VIOLATION"):
        check_pricing_guardrails("Get this shirt for a 20% discount today!")

    # Should raise error on USD cost
    with pytest.raises(ValueError, match="GUARDRAIL VIOLATION"):
        check_pricing_guardrails("Price is 100 USD.")

def test_suggestions_valid_input():
    state: AssistantState = {
        "cart": [{"item_id": "c3", "name": "White Linen Shirt", "category": "shirt"}],
        "clicks": ["c1"],
        "previous_chats": ["Prefers minimal styling"],
        "chat_history": []
    }
    
    result = generate_daily_suggestions(state)
    assert "suggestions" in result
    assert len(result["suggestions"]) == 1
    
    suggestion_text = result["suggestions"][0]
    assert "Style" in suggestion_text or "Coordinate" in suggestion_text
    # Ensure no prices were outputted
    assert "$" not in suggestion_text
    assert "USD" not in suggestion_text
    assert "price" not in suggestion_text.lower()

def test_suggestions_invalid_input_price():
    # Input has a price key, which should fail input validation
    state: AssistantState = {
        "cart": [{"item_id": "c3", "name": "White Linen Shirt", "price": "45"}],
        "clicks": [],
        "previous_chats": [],
        "chat_history": []
    }
    
    with pytest.raises(ValueError, match="INPUT STATE ERROR"):
        generate_daily_suggestions(state)
