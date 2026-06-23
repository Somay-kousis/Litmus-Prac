import os
import json
from pathlib import Path
from typing import List, Optional, TypedDict, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Load .env file from the Cars/ root directory to enable Groq and LangSmith tracking
dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Verify API key presence (Fail loudly)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "CRITICAL ERROR: GROQ_API_KEY is not defined in environment variables or Cars/.env file. "
        "Please provide a valid Groq API key."
    )

# Model definitions adhering to user's strict tier limits:
# 1. Standard model for plain text string output (not versatile)
llm_text = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=GROQ_API_KEY
)

# 2. Versatile model ONLY used for structured output definitions
llm_structured = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    groq_api_key=GROQ_API_KEY
)

# Pydantic Schema for Query Intent Extraction (Structured Output)
class UserIntent(BaseModel):
    focus_specs: List[str] = Field(
        description="Specifications to prioritize (e.g. price, horsepower, torque, rangeOrMileage, seating)"
    )
    driving_context: str = Field(
        description="Explanation of the real-world driving environment requested (e.g. track speed, winter grip, cargo space)."
    )

# Chat message format
class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str

# Define State Schema
class AgentState(TypedDict):
    selected_cars: List[dict]
    user_query: Optional[str]
    mode: str
    analysis: Optional[str]
    iterations: int
    hitl_approved: bool
    hitl_feedback: Optional[str]
    chat_history: List[ChatMessage]
    summary: Optional[str]

# Sliding window limit configuration
HISTORY_LIMIT = 50

# Node 1: Input Validation & History Entry
def validate_input(state: AgentState) -> dict:
    if not state.get("selected_cars") or len(state["selected_cars"]) < 1:
        raise ValueError("Graph execution error: At least one car specification dictionary must be provided.")
        
    history = list(state.get("chat_history") or [])
    
    # Capture user input entry
    if state.get("user_query"):
        user_msg: ChatMessage = {"role": "user", "content": state["user_query"]}
        if not history or history[-1]["content"] != state["user_query"]:
            history.append(user_msg)
    elif state.get("mode") == "automatic":
        car_names = ", ".join([f"{c['brand']} {c['model']}" for c in state["selected_cars"]])
        auto_msg: ChatMessage = {"role": "user", "content": f"Automatic comparison requested for: {car_names}"}
        if not history or history[-1]["content"] != auto_msg["content"]:
            history.append(auto_msg)
            
    return {"chat_history": history}

# Router for Automatic vs Manual flow
def route_mode(state: AgentState) -> str:
    if state.get("mode") == "automatic":
        return "generate_auto_comparison"
    else:
        return "generate_manual_comparison"

# Helper to serialize specifications block for LLM prompts
def format_cars_for_prompt(cars: List[dict]) -> str:
    formatted = []
    for car in cars:
        specs = car["specs"]
        formatted.append(
            f"Car: {car['brand']} {car['model']} ({car['year']})\n"
            f"- Price: ${car['price']:,}\n"
            f"- Body Type: {car['bodyType']}\n"
            f"- Fuel Type: {car['fuelType']}\n"
            f"- Drivetrain: {car['drivetrain']}\n"
            f"- Transmission: {car['transmission']}\n"
            f"- Power: {specs['horsepower']} HP\n"
            f"- Torque: {specs['torque']}\n"
            f"- 0-60 mph Acceleration: {specs['acceleration']}\n"
            f"- Top Speed: {specs['topSpeed']}\n"
            f"- Economy/Range: {specs['rangeOrMileage']}\n"
            f"- Engine/Motor details: {specs['engine']}\n"
            f"- Seating: {specs['seating']}\n"
            f"- Cargo space: {specs['cargoVolume']}\n"
            f"- Highlights: {', '.join(car['features'])}"
        )
    return "\n\n".join(formatted)

# Node 2: Generate Automatic Comparison (uses llama-3.1-8b-instant for string output)
def generate_auto_comparison(state: AgentState) -> dict:
    cars = state["selected_cars"]
    cars_data = format_cars_for_prompt(cars)
    
    system_prompt = (
        "You are an expert automotive systems analyst. Translate numeric specifications "
        "into clear, real-world driving implications for the user (e.g. how horsepower affects "
        "highway passing, how AWD affects traction, how torque affects acceleration feel, and fuel/power choice daily impact).\n"
        "STRICT RULE: Do NOT hallucinate values or make up comparisons not justified by the specifications. Be objective."
    )
    
    user_prompt = (
        f"Generate a side-by-side real-world comparison report based on these specifications:\n\n"
        f"{cars_data}\n\n"
        f"Organize your answer into clean Markdown sections:\n"
        f"1. **Performance & Acceleration Feel**\n"
        f"2. **Handling, Grip & Drivetrain Practicality**\n"
        f"3. **Cabin Space, Seating & Range Utility**"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = llm_text.invoke(messages)
    return {"analysis": response.content, "iterations": state.get("iterations", 0) + 1}

# Node 3: Generate Manual Response (uses llama-3.3-70b-versatile for parser, llama-3.1-8b-instant for report)
def generate_manual_comparison(state: AgentState) -> dict:
    cars = state["selected_cars"]
    query = state.get("user_query", "")
    cars_data = format_cars_for_prompt(cars)
    
    # Retrieve RAG context (local documents retrieval)
    from app.rag import retrieve_car_context
    rag_context = retrieve_car_context(query, k=2)
    
    # STEP 1: Parsed structured intent using versatile model
    intent_parser = llm_structured.with_structured_output(UserIntent)
    intent = intent_parser.invoke(
        f"Extract key spec focuses and real-world context for this query: '{query}'"
    )
    
    # STEP 2: Use parsed intent to build string response with standard model
    system_prompt = (
        "You are a professional car reviewer answering a user query. Compare specifications of target "
        "vehicles focusing on parameters that answer the user's specific context. Translate numbers into daily driving feel.\n"
        "STRICT RULE: Focus specifically on criteria requested in the query intent. Do not hallucinate."
    )
    
    user_prompt = (
        f"Comparison Cars:\n\n{cars_data}\n\n"
        f"User Query: '{query}'\n"
        f"Extracted Intent Context: '{intent.driving_context}'\n"
        f"Focus parameters: {', '.join(intent.focus_specs)}\n\n"
        f"Retrieved Technical Documentation Context:\n{rag_context}\n\n"
        f"Provide a comparative review directly answering the user query. Reference specs and the retrieved technical documentation context explicitly where helpful."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = llm_text.invoke(messages)
    return {"analysis": response.content, "iterations": state.get("iterations", 0) + 1}

# Node 4: Human review validation point
def human_review(state: AgentState) -> dict:
    # A no-op node that functions as an interrupt anchor in the graph pipeline
    return {}

# Routing decision after human review
def route_approval(state: AgentState) -> str:
    if state.get("hitl_approved") is True or state.get("iterations", 0) >= 3:
        return "finalize_response"
    else:
        return "revise_comparison"

# Node 5: Revise Analysis based on feedback (uses llama-3.1-8b-instant for string output)
def revise_comparison(state: AgentState) -> dict:
    feedback = state.get("hitl_feedback", "Adjust formatting")
    current_analysis = state.get("analysis", "")
    
    system_prompt = (
        "You are an editor. Revise the generated car comparison review based on human supervisor feedback. "
        "Retain the technical specs validation and do not hallucinate."
    )
    
    user_prompt = (
        f"Current Review:\n\n{current_analysis}\n\n"
        f"Supervisor Reviewer Feedback: '{feedback}'\n\n"
        f"Provide a revised review report integrating this feedback."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response = llm_text.invoke(messages)
    return {
        "analysis": response.content,
        "iterations": state.get("iterations", 0) + 1,
        "hitl_approved": True # Mark approved after revision integration
    }

# Node 6: Finalize Response & Compress Memory Window
def finalize_response(state: AgentState) -> dict:
    history = list(state.get("chat_history") or [])
    analysis = state.get("analysis") or ""
    summary = state.get("summary")
    
    # Append assistant response
    history.append({"role": "assistant", "content": analysis})
    
    # Memory Consolidation / Compression Loop
    while len(history) > HISTORY_LIMIT:
        oldest = history.pop(0)
        role = oldest["role"].upper()
        content = oldest["content"]
        
        snippet = content[:80] + "..." if len(content) > 80 else content
        
        if not summary:
            summary = f"[{role}]: {snippet}"
        else:
            summary = f"({summary} + [{role}]: {snippet})"
            
    return {
        "chat_history": history,
        "summary": summary
    }

# Build and Compile Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("validate_input", validate_input)
workflow.add_node("generate_auto_comparison", generate_auto_comparison)
workflow.add_node("generate_manual_comparison", generate_manual_comparison)
workflow.add_node("human_review", human_review)
workflow.add_node("revise_comparison", revise_comparison)
workflow.add_node("finalize_response", finalize_response)

# Set up edges
workflow.set_entry_point("validate_input")

workflow.add_conditional_edges(
    "validate_input",
    route_mode,
    {
        "generate_auto_comparison": "generate_auto_comparison",
        "generate_manual_comparison": "generate_manual_comparison"
    }
)

workflow.add_edge("generate_auto_comparison", "human_review")
workflow.add_edge("generate_manual_comparison", "human_review")

workflow.add_conditional_edges(
    "human_review",
    route_approval,
    {
        "finalize_response": "finalize_response",
        "revise_comparison": "revise_comparison"
    }
)

workflow.add_edge("revise_comparison", "human_review")
workflow.add_edge("finalize_response", END)

# Compile with Memory Checkpointer (Removed MemorySaver from global agent_graph for LangGraph Dev Server compatibility)
agent_graph = workflow.compile(
    interrupt_before=["human_review"]
)
