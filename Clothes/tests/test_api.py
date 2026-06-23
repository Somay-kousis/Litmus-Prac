import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.prompts.templates import REFUSAL_RESPONSE

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "AURA STYLING" in response.text

def test_api_suggestions_success():
    payload = {
        "cart": [
            {"item_id": "c3", "name": "White Linen Shirt", "category": "shirt", "color": "white", "size": "M"}
        ],
        "clicks": ["c1"],
        "previous_chats": ["Enjoys white linen clothing"]
    }
    response = client.post("/suggestions", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
    assert "$" not in data["suggestions"][0]

def test_api_suggestions_failure_price():
    # Input has 'price' key inside cart item
    payload = {
        "cart": [
            {"item_id": "c3", "name": "White Linen Shirt", "category": "shirt", "color": "white", "size": "M", "price": "45"}
        ],
        "clicks": [],
        "previous_chats": []
    }
    response = client.post("/suggestions", json=payload)
    assert response.status_code == 422
    assert "forbidden pricing" in response.text.lower()

def test_api_chat_success():
    payload = {
        "user_query": "What goes well with white linen shirt?",
        "cart": [
            {"item_id": "c3", "name": "White Linen Shirt", "category": "shirt", "color": "white", "size": "M"}
        ],
        "clicks": [],
        "previous_chats": [],
        "chat_history": []
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "chat_history" in data
    assert len(data["chat_history"]) == 2
    assert "$" not in data["response"]

def test_api_chat_guardrail_refusal():
    payload = {
        "user_query": "Do you have any active coupons or cheap discounts on jackets?",
        "cart": [],
        "clicks": [],
        "previous_chats": [],
        "chat_history": []
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == REFUSAL_RESPONSE

def test_api_chat_recipient_memory():
    payload = {
        "user_query": "I am shopping for my dad",
        "cart": [{"item_id": "c3", "name": "White Linen Shirt", "category": "shirt", "color": "white", "size": "M"}],
        "clicks": [],
        "previous_chats": [],
        "chat_history": [],
        "recipient": "self",
        "recipient_profiles": {}
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recipient"] == "dad"
    # Ensure profile keys exist in response
    assert "recipient_profiles" in data
    assert "dad" in data["recipient_profiles"]
