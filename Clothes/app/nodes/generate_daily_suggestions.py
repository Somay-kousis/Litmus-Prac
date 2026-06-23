import re
from typing import Dict, Any, List
from app.graph.state import AssistantState
from app.models.llm import llm_text
from app.prompts.templates import DAILY_SUGGESTIONS_SYSTEM, GUARDRAIL_INSTRUCTIONS
from app.data.db_store import db_store

# Mock clothing catalog (no pricing info allowed)
CLOTHING_CATALOG = [
    {"item_id": "c1", "name": "Classic Denim Jacket", "category": "jacket", "color": "blue", "size": "M/L/XL"},
    {"item_id": "c2", "name": "Slim Fit Beige Chinos", "category": "pants", "color": "beige", "size": "S/M/L/XL"},
    {"item_id": "c3", "name": "White Linen Shirt", "category": "shirt", "color": "white", "size": "M/L/XL"},
    {"item_id": "c4", "name": "Black Leather Boots", "category": "shoes", "color": "black", "size": "9/10/11"},
    {"item_id": "c5", "name": "Minimalist Crewneck Tee", "category": "shirt", "color": "grey", "size": "S/M/L"},
    {"item_id": "c6", "name": "Khaki Utility Jacket", "category": "jacket", "color": "khaki", "size": "M/L"},
]

def check_pricing_guardrails(text: str) -> None:
    """Checks string content for potential price or discount mentions, raising ValueError if found."""
    # Pattern to search for currency symbols or pricing keywords (price, cost, discount, sale, USD, coupon, off)
    price_patterns = [
        r"\$\d+",                      # e.g. $10, $5.99
        r"\d+\s*(USD|USDs|INR|Rupees|dollars|cents)", # e.g. 50 USD, 100 Rupees
        r"\b(price|pricing|cost|costs|discount|discounts|sale|sales|coupon|coupons|promo|promotions|percent\s*off|%off)\b"
    ]
    
    for pattern in price_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError(
                f"GUARDRAIL VIOLATION: Discussion or display of prices, costs, discounts, or promotions is forbidden. "
                f"Detected forbidden pattern matching '{pattern}' in text: {text[:100]}..."
            )

def generate_daily_suggestions(state: AssistantState) -> Dict[str, Any]:
    # 1. Input state validation (Fail loudly)
    cart = state.get("cart") or []
    clicks = state.get("clicks") or []
    previous_chats = state.get("previous_chats") or []

    # Ensure no cart item contains price/cost/discount fields
    for item in cart:
        for key, val in item.items():
            if any(forbidden in str(key).lower() for forbidden in ["price", "cost", "discount", "sale"]):
                raise ValueError(f"INPUT STATE ERROR: Cart item key '{key}' contains forbidden pricing term.")
            if any(forbidden in str(val).lower() for forbidden in ["$", "usd", "inr", "discount"]):
                raise ValueError(f"INPUT STATE ERROR: Cart item value for '{key}' contains forbidden pricing term.")

    # Fetch "self" profile details from mock e-commerce database (RAG Context)
    db_profile = db_store.get_profile("self")
    db_profile_str = f"""
    Customer Styling Profile context from Database:
    - Liked styles/colors/brands: {db_profile.get('likes')}
    - Disliked styles/colors/patterns: {db_profile.get('dislikes')}
    - Past purchases: {db_profile.get('purchases')}
    """

    # 2. Format catalog for LLM prompt
    catalog_str = "\n".join([
        f"- ID: {item['item_id']} | {item['name']} (Category: {item['category']}, Color: {item['color']}, Sizes: {item['size']})"
        for item in CLOTHING_CATALOG
    ])

    # 3. Format cart and clicks context
    cart_str = ", ".join([item.get("name", "Unknown Item") for item in cart]) if cart else "Empty Cart"
    clicks_str = ", ".join(clicks) if clicks else "No recent clicks"
    chats_str = " | ".join(previous_chats) if previous_chats else "No prior history"

    # 4. Construct prompt
    system_prompt = DAILY_SUGGESTIONS_SYSTEM.format(guardrail_instructions=GUARDRAIL_INSTRUCTIONS)
    user_prompt = f"""
{db_profile_str}

Here is the user's styling context:
- Current Cart Items: {cart_str}
- Recent Clicks/Views: {clicks_str}
- Previous Interactions Summary: {chats_str}

Here is our available catalog of clothing items:
{catalog_str}

Analyze this context and output daily personalized clothing recommendations. Focus on coordinates that fit together.
Strictly adhere to the user's likes and avoid dislikes (e.g. do not suggest items matching their dislikes, like neon or high print).
Do NOT include prices or discounts!
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # 5. Call LLM
    response = llm_text.invoke(messages)
    content = response.content

    # 6. Output validation (Fail loudly)
    check_pricing_guardrails(content)

    return {"suggestions": [content]}
