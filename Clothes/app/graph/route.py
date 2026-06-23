from app.graph.state import AssistantState

def route_mode(state: AssistantState) -> str:
    """Routes the execution path to automated suggestions or manual chat node."""
    mode = state.get("mode")
    if mode == "automated":
        return "generate_daily_suggestions"
    elif mode == "manual":
        return "chat_assistant"
    else:
        raise ValueError(
            f"GRAPH ROUTING ERROR: State must contain a valid 'mode' (either 'automated' or 'manual'). Received: '{mode}'"
        )
