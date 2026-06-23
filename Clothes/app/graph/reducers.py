from typing import List, Any, Dict

def merge_lists(left: List[Any], right: List[Any]) -> List[Any]:
    """Appends elements to a list, maintaining order and preventing duplicates if elements are hashable."""
    if left is None:
        left = []
    if right is None:
        right = []
    
    result = list(left)
    for item in right:
        if item not in result:
            result.append(item)
    return result

def merge_messages(left: List[Dict[str, str]], right: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Updates the chat history. If a new history list is provided, it replaces the existing list to support truncation and compression."""
    if right is not None:
        return right
    return left if left is not None else []

def merge_dict(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Combines dictionaries of recipient style profiles, overwriting existing keys with updated properties."""
    if left is None:
        left = {}
    if right is None:
        right = {}
    
    result = dict(left)
    for key, value in right.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dict(result[key], value)
        else:
            result[key] = value
    return result
