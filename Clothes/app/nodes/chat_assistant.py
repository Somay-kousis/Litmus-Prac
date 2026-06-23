import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.graph.state import AssistantState
from app.models.llm import llm_text, llm_structured
from app.prompts.templates import CHAT_ASSISTANT_SYSTEM, GUARDRAIL_INSTRUCTIONS, REFUSAL_RESPONSE
from app.nodes.generate_daily_suggestions import check_pricing_guardrails, CLOTHING_CATALOG
from app.data.db_store import db_store

# Pydantic model for structured e-commerce styling preference extraction
class RecipientMetadata(BaseModel):
    recipient: Optional[str] = Field(
        None,
        description="The relationship or name of the person being shopped for (e.g. 'self', 'brother', 'wife', 'mom', 'friend'). Set to 'self' if they say 'myself', 'me', or 'for myself'."
    )
    style_preference_updated: Optional[str] = Field(
        None,
        description="General sizing or style description sentences mentioned in the user message for this recipient."
    )
    new_likes: List[str] = Field(
        default=[],
        description="List of specific clothing styles, materials, colors, or brands they explicitly like/love (e.g. 'black color', 'Cantabil brand')."
    )
    new_dislikes: List[str] = Field(
        default=[],
        description="List of specific styles, patterns, colors, or brands they explicitly dislike/hate/avoid (e.g. 'high print', 'neon colors')."
    )
    new_sizing: Dict[str, str] = Field(
        default={},
        description="Updates to size properties (e.g. {'top': 'S', 'bottom': 'M', 'shoes': '10'}) mentioned in text."
    )
    new_wardrobe_items: List[str] = Field(
        default=[],
        description="Specific clothing items the user explicitly mentions they already own (e.g. 'grey jacket', 'black tee', 'white sneakers')."
    )
    new_pieces_needed: Optional[int] = Field(
        None,
        description="The total number of clothing pieces the user is targeting to purchase (e.g. 'I want to buy 4 items')."
    )
    new_occupation: Optional[str] = Field(
        None,
        description="The user's professional role or occupation (e.g. 'developer', 'designer', 'teacher') mentioned in chat."
    )

def is_pricing_query(text: str) -> bool:
    """Detects if the query asks about price, discounts, sales, shipping or costs."""
    price_patterns = [
        r"\$",
        r"\b(price|pricing|cost|costs|discount|discounts|sale|sales|coupon|coupons|promo|promotions|shipping|worth|cheap|expensive|how\s+much)\b"
    ]
    for pattern in price_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def chat_assistant(state: AssistantState) -> Dict[str, Any]:
    # 1. Validate inputs (Fail loudly)
    query = state.get("user_query")
    if not query:
        raise ValueError("INPUT STATE ERROR: user_query must not be empty in chat_assistant node.")

    cart = state.get("cart") or []
    clicks = state.get("clicks") or []
    previous_chats = state.get("previous_chats") or []
    chat_history = state.get("chat_history") or []
    recipient_profiles = state.get("recipient_profiles") or {}
    current_recipient = state.get("recipient")

    # Guardrail check on inputs
    for item in cart:
        for key, val in item.items():
            if any(forbidden in str(key).lower() for forbidden in ["price", "cost", "discount", "sale"]):
                raise ValueError(f"INPUT STATE ERROR: Cart item key '{key}' contains forbidden pricing term.")

    # 2. Check if the user query violates guardrails (Pre-check)
    if is_pricing_query(query):
        return {"response": REFUSAL_RESPONSE}

    # 3. Rule 1: Begin chat with greeting if history is empty
    if not chat_history and query.strip().lower() in ["hi", "hello", "hey", "hola", "greetings", "start"]:
        return {
            "response": "Hey, who are we looking for clothes for today?",
            "recipient": "self"
        }

    # 4. Extract metadata using structured model
    metadata_parser = llm_structured.with_structured_output(RecipientMetadata)
    extraction_prompt = f"""
    Analyze the user's styling message:
    User Query: "{query}"
    
    Current Recipient: "{current_recipient or 'self'}"
    
    Extract:
    1. recipient: Who they are buying clothes for. If they say "someone else", "my brother", "my girlfriend", "my friend", extract the relation/name. If they say "myself" or "me", it is "self".
    2. style_preference_updated: Any style preferences or sizes mentioned.
    3. new_likes: List of colors, brands, designs, or fabrics they like/love.
    4. new_dislikes: List of colors, designs, fabrics, or patterns (like high print) they dislike/hate.
    5. new_sizing: Sizing dict if mentioned (top/bottom/shoes).
    6. new_wardrobe_items: List of items they mention they already own (e.g. 'grey jacket', 'white sneakers').
    7. new_pieces_needed: Number of items they need to buy.
    8. new_occupation: Their job/role (e.g. 'developer').
    """
    
    try:
        extracted = metadata_parser.invoke(extraction_prompt)
        recipient = extracted.recipient or current_recipient or "self"
        style_pref = extracted.style_preference_updated
        new_likes = extracted.new_likes
        new_dislikes = extracted.new_dislikes
        new_sizing = extracted.new_sizing
        new_wardrobe_items = extracted.new_wardrobe_items
        new_pieces_needed = extracted.new_pieces_needed
        new_occupation = extracted.new_occupation
    except Exception:
        recipient = current_recipient or "self"
        style_pref = None
        new_likes = []
        new_dislikes = []
        new_sizing = {}
        new_wardrobe_items = []
        new_pieces_needed = None
        new_occupation = None

    # Normalize recipient key
    norm_recipient = recipient.lower().strip()
    if norm_recipient in ["me", "myself", "self"]:
        norm_recipient = "self"

    # Write extracted preferences to the local persistent e-commerce database
    for like in new_likes:
        db_store.add_preference(norm_recipient, "likes", like)
    for dislike in new_dislikes:
        db_store.add_preference(norm_recipient, "dislikes", dislike)
    for item in new_wardrobe_items:
        db_store.add_wardrobe_item(norm_recipient, item)
    if new_sizing:
        db_store.update_sizing(norm_recipient, new_sizing)
    if new_pieces_needed is not None:
        db_store.update_shopping_goals(norm_recipient, {"pieces_needed": new_pieces_needed})
    if new_occupation:
        db_store.update_occupation(norm_recipient, new_occupation)

    # Fetch updated profile from local database (True RAG Context)
    db_profile = db_store.get_profile(norm_recipient)

    # Handle transient profile state (recipient_profiles)
    profiles_update = dict(recipient_profiles)
    if norm_recipient not in profiles_update:
        profiles_update[norm_recipient] = {}
    
    # Retrieve preferences from both database and the transient state recipient_profiles
    state_pref = recipient_profiles.get(norm_recipient, {}).get("preferences")
    
    # Check if we have preferences for this person in either store
    has_profile_data = (
        len(db_profile.get("likes", [])) > 0 or 
        len(db_profile.get("sizing", {})) > 0 or 
        len(db_profile.get("wardrobe", [])) > 0 or
        bool(state_pref)
    )

    # Store likes/dislikes/sizing/wardrobe strings inside the response metadata preferences
    pref_summary = []
    if db_profile.get("likes"):
        pref_summary.append(f"Loves: {', '.join(db_profile['likes'])}")
    if db_profile.get("dislikes"):
        pref_summary.append(f"Hates: {', '.join(db_profile['dislikes'])}")
    if db_profile.get("sizing"):
        pref_summary.append(f"Sizes: {db_profile['sizing']}")
    if db_profile.get("wardrobe"):
        pref_summary.append(f"Owns: {', '.join(db_profile['wardrobe'])}")
        
    profiles_update[norm_recipient]["preferences"] = " | ".join(pref_summary) if pref_summary else (state_pref or style_pref)

    # Handle "someone else" generic prompt
    if norm_recipient != "self":
        if norm_recipient in ["someone else", "someone", "another person"]:
            return {
                "response": "Who who? Who are we shopping for today?",
                "recipient": recipient,
                "recipient_profiles": profiles_update
            }
        
        if not has_profile_data and not style_pref:
            response_text = f"Got it! Since we are shopping for your {recipient}, the items in your current cart won't be used (they are for you!). Tell me: what is their style preference and size so I can make coordinate recommendations?"
            return {
                "response": response_text,
                "recipient": recipient,
                "recipient_profiles": profiles_update
            }
        
        elif has_profile_data and not style_pref:
            pref_details = profiles_update[norm_recipient]["preferences"]
            response_text = f"Ah, your {recipient}! I remember their profile: {pref_details}. Since we're shopping for them, I will ignore your current cart. What styling coordinate recommendations or items are we looking to pick for them today?"
            return {
                "response": response_text,
                "recipient": recipient,
                "recipient_profiles": profiles_update
            }

    # 5. Core style advice generation using standard llm_text
    cart_str = ", ".join([item.get("name", "Unknown Item") for item in cart]) if cart else "Empty Cart"
    clicks_str = ", ".join(clicks) if clicks else "No recent clicks"
    
    summary_prefix = f"Summary of past conversation: {state.get('summary')}\n" if state.get("summary") else ""
    
    history_str = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Stylist"
        history_str += f"{role}: {msg['content']}\n"

    catalog_str = "\n".join([
        f"- ID: {item['item_id']} | {item['name']} (Category: {item['category']}, Color: {item['color']}, Sizes: {item['size']})"
        for item in CLOTHING_CATALOG
    ])

    system_prompt = CHAT_ASSISTANT_SYSTEM.format(guardrail_instructions=GUARDRAIL_INSTRUCTIONS)
    
    db_profile_str = f"""
Customer Profile Context from Database:
- Relationship: {db_profile.get('relationship')}
- Sizing Details: {db_profile.get('sizing')}
- Stored Likes/Preferences: {db_profile.get('likes')}
- Stored Dislikes/Restrictions: {db_profile.get('dislikes')}
- Stored Past Purchases: {db_profile.get('purchases')}
- Stored Wardrobe (Items Already Owned): {db_profile.get('wardrobe')}
- Shopping Goals (Target Pieces): {db_profile.get('shopping_goals')}
- Occupation: {db_profile.get('occupation')}
"""

    wardrobe_rules = f"""
STRICT WARDROBE CONTRAST & UPGRADE RULES:
1. Look closely at "Stored Wardrobe (Items Already Owned)" above.
2. If the user asks about an item they already own (e.g. if they ask "how about the grey jacket" or suggest an item matching one they own), you MUST refuse/contrast it by replying: "Don't you already have that [item]?" and immediately suggest a complementary or different item from the catalog to make their wardrobe++ (e.g., "Don't you already have that grey jacket? Let's check out the Khaki Utility Jacket or White Linen Shirt instead to make your wardrobe++").
3. Check the "Shopping Goals (Target Pieces)" pieces_needed count. Keep track of how many items are currently in their cart (Cart Count: {len(cart)}) versus how many they need. Give them a friendly progress check.
4. If their "Occupation" is listed (e.g., 'developer'), customize your styling advice to match their occupation's vibe (e.g. developers prefer comfortable, functional, minimal, yet smart outfits).
"""

    if norm_recipient != "self":
        user_prompt = f"""
{summary_prefix}
The user is shopping for their {recipient} (NOT themselves).
IGNORE the current cart items (they are for the user).

{db_profile_str}

{wardrobe_rules}

Recent Clicks: {clicks_str}

Conversation History so far:
{history_str}

Available Clothing Catalog:
{catalog_str}

User Query: {query}

Provide styling recommendations for the user's {recipient} using the catalog. Coordinate compatible items. Do NOT mention prices or discounts!
"""
    else:
        user_prompt = f"""
{summary_prefix}
The user is shopping for themselves.

{db_profile_str}

{wardrobe_rules}

Current Cart: {cart_str}
Recent Clicks: {clicks_str}

Conversation History so far:
{history_str}

Available Clothing Catalog:
{catalog_str}

User Query: {query}

Provide styling opinions on the cart items or coordinate recommendations using the catalog. Adhere strictly to preferences. Do NOT mention prices or discounts!
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = llm_text.invoke(messages)
    content = response.content

    check_pricing_guardrails(content)

    return {
        "response": content,
        "recipient": recipient,
        "recipient_profiles": profiles_update
    }
