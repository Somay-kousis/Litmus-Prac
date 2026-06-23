from typing import Annotated, Dict, List, Any
from typing_extensions import NotRequired, TypedDict
from app.graph.reducers import merge_lists, merge_messages, merge_dict

class AssistantState(TypedDict):
    # Current cart items (each item is Dict[str, Any] with item_id, name, category, color, size, etc.)
    cart: Annotated[List[Dict[str, Any]], merge_lists]
    
    # Click history (list of item IDs or categories)
    clicks: Annotated[List[str], merge_lists]
    
    # Previous chats summary/history strings
    previous_chats: Annotated[List[str], merge_lists]
    
    # The current query inputted by the user in manual chat
    user_query: NotRequired[str]
    
    # Interactive chat history (list of dicts with role, content)
    chat_history: Annotated[List[Dict[str, str]], merge_messages]
    
    # The current execution mode: 'automated' or 'manual'
    mode: NotRequired[str]
    
    # Who are we shopping for (e.g. 'self', 'brother', 'wife')
    recipient: NotRequired[str]

    # Stored style profiles for different recipients (maps relation/name to style preferences, e.g., sizes, colors)
    recipient_profiles: Annotated[Dict[str, Any], merge_dict]

    # Compressed message summary window for long chats
    summary: NotRequired[str]

    # Generated daily suggestions output
    suggestions: NotRequired[List[str]]
    
    # Final generated chat response output
    response: NotRequired[str]
