import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.agent import workflow
from app.schemas import CompareRequest, CompareResponse, ReviewRequest, Message
from langgraph.checkpoint.memory import MemorySaver

# Compile graph locally with checkpointer for FastAPI endpoints persistence
memory = MemorySaver()
agent_graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)

app = FastAPI(title="DriveMatrix Comparison Agent Backend")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "DriveMatrix Backend Agent is Live."}

@app.post("/compare/start", response_model=CompareResponse)
def compare_start(request: CompareRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initialize the input state with chat history and summary
    initial_state = {
        "selected_cars": [car.model_dump() for car in request.cars],
        "user_query": request.user_query,
        "mode": request.mode,
        "iterations": 0,
        "hitl_approved": False,
        "hitl_feedback": None,
        "analysis": None,
        "chat_history": [msg.model_dump() for msg in request.chat_history] if request.chat_history else [],
        "summary": request.summary
    }
    
    try:
        # Run graph. It will pause/interrupt right before "human_review"
        agent_graph.invoke(initial_state, config)
        
        # Fetch state details after interrupt
        state_info = agent_graph.get_state(config)
        state_values = state_info.values
        
        # Check if it is currently waiting/paused
        requires_review = "human_review" in state_info.next
        
        return CompareResponse(
            thread_id=thread_id,
            mode=request.mode,
            analysis=state_values.get("analysis"),
            requires_review=requires_review,
            hitl_approved=state_values.get("hitl_approved", False),
            iterations=state_values.get("iterations", 0),
            feedback_needed=state_values.get("hitl_feedback"),
            chat_history=[Message(role=m["role"], content=m["content"]) for m in state_values.get("chat_history", [])],
            summary=state_values.get("summary")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Execution Error: {str(e)}")

@app.post("/compare/review", response_model=CompareResponse)
def compare_review(thread_id: str, request: ReviewRequest):
    config = {"configurable": {"thread_id": thread_id}}
    
    # Get current state from checkpoint memory saver
    state_info = agent_graph.get_state(config)
    if not state_info.values:
        raise HTTPException(status_code=404, detail="Thread execution state not found.")
        
    try:
        # Update state check pointer with the review verdict
        agent_graph.update_state(
            config,
            {
                "hitl_approved": request.approved,
                "hitl_feedback": request.feedback
            },
            as_node="human_review"
        )
        
        # Resume graph execution (input=None tells it to resume from current checkpoint)
        agent_graph.invoke(None, config)
        
        # Fetch updated state
        updated_state = agent_graph.get_state(config)
        updated_values = updated_state.values
        requires_review = "human_review" in updated_state.next
        
        return CompareResponse(
            thread_id=thread_id,
            mode=updated_values.get("mode"),
            analysis=updated_values.get("analysis"),
            requires_review=requires_review,
            hitl_approved=updated_values.get("hitl_approved", False),
            iterations=updated_values.get("iterations", 0),
            feedback_needed=updated_values.get("hitl_feedback"),
            chat_history=[Message(role=m["role"], content=m["content"]) for m in updated_values.get("chat_history", [])],
            summary=updated_values.get("summary")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Resume Error: {str(e)}")
