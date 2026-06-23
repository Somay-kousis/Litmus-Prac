from langgraph.graph import StateGraph, START, END
from app.graph.state import AssistantState
from app.graph.route import route_mode
from app.nodes.generate_daily_suggestions import generate_daily_suggestions
from app.nodes.chat_assistant import chat_assistant

def validate_input(state: AssistantState) -> dict:
    """Pre-validation node to ensure correct inputs and state configuration."""
    mode = state.get("mode")
    if not mode:
        raise ValueError("GRAPH INPUT ERROR: 'mode' is required in state.")
    
    if mode not in ["automated", "manual"]:
        raise ValueError(f"GRAPH INPUT ERROR: 'mode' must be 'automated' or 'manual'. Got '{mode}'.")
        
    if mode == "manual":
        query = state.get("user_query")
        if not query or not query.strip():
            raise ValueError("GRAPH INPUT ERROR: 'user_query' is required in 'manual' mode.")
            
    return {}

def finalize_response(state: AssistantState) -> dict:
    """Appends current manual chat interaction and implements parenthetical sliding window memory compression."""
    mode = state.get("mode")
    if mode == "manual":
        query = state.get("user_query")
        response = state.get("response")
        history = list(state.get("chat_history") or [])
        summary = state.get("summary")
        
        if query and response:
            history.append({"role": "user", "content": query})
            history.append({"role": "assistant", "content": response})
            
            # Compress oldest messages if history exceeds the 50 message limit (25 turns)
            while len(history) > 50:
                oldest = history.pop(0)
                role = oldest["role"].upper()
                content = oldest["content"]
                
                # Compress into: ( ( S + 1 ) + 2 ) parenthetical structure
                msg_str = f"[{role}]: {content}"
                if not summary:
                    summary = msg_str
                else:
                    summary = f"({summary} + {msg_str})"
            
            return {
                "chat_history": history,
                "summary": summary
            }
    return {}

# 1. Initialize State Graph
workflow = StateGraph(AssistantState)

# 2. Add Nodes
workflow.add_node("validate_input", validate_input)
workflow.add_node("generate_daily_suggestions", generate_daily_suggestions)
workflow.add_node("chat_assistant", chat_assistant)
workflow.add_node("finalize_response", finalize_response)

# 3. Add Edges and Routing
workflow.set_entry_point("validate_input")

workflow.add_conditional_edges(
    "validate_input",
    route_mode,
    {
        "generate_daily_suggestions": "generate_daily_suggestions",
        "chat_assistant": "chat_assistant"
    }
)

workflow.add_edge("generate_daily_suggestions", END)
workflow.add_edge("chat_assistant", "finalize_response")
workflow.add_edge("finalize_response", END)

# 4. Compile the Graph
agent_graph = workflow.compile()
