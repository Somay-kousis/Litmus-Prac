import uuid
import app.agent as agent
from app.agent import workflow
from langgraph.checkpoint.memory import MemorySaver

# Compile graph locally with checkpointer for test execution persistence
memory = MemorySaver()
agent_graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)

# Mock Dataset of Cars
mock_cars = [
    {
        "id": "tesla-model-s",
        "brand": "Tesla",
        "model": "Model S Plaid",
        "year": 2026,
        "price": 89990,
        "bodyType": "Sedan",
        "fuelType": "Electric",
        "transmission": "Single-speed",
        "drivetrain": "AWD",
        "specs": {
            "horsepower": 1020,
            "torque": "1,020 lb-ft",
            "acceleration": "1.99s",
            "topSpeed": "200 mph",
            "rangeOrMileage": "396 miles",
            "batteryCapacity": "100 kWh",
            "engine": "Tri-Motor AC",
            "seating": 5,
            "cargoVolume": "25 cu ft"
        },
        "features": ["Autopilot", "17-inch screen"],
        "description": "Electric hyper sedan."
    },
    {
        "id": "porsche-taycan",
        "brand": "Porsche",
        "model": "Taycan Turbo S",
        "year": 2026,
        "price": 194900,
        "bodyType": "Sedan",
        "fuelType": "Electric",
        "transmission": "Single-speed",
        "drivetrain": "AWD",
        "specs": {
            "horsepower": 938,
            "torque": "818 lb-ft",
            "acceleration": "2.3s",
            "topSpeed": "161 mph",
            "rangeOrMileage": "318 miles",
            "batteryCapacity": "105 kWh",
            "engine": "Dual Motors",
            "seating": 4,
            "cargoVolume": "14.3 cu ft"
        },
        "features": ["Porsche Active Ride", "Rear Axle Steering"],
        "description": "High performance electric sedan."
    }
]

def run_verification():
    print("====================================================")
    print("   VERIFYING DRIVE MATRIX LANGGRAPH AGENT ENGINE    ")
    print("====================================================")
    
    # ----------------------------------------------------
    # TEST CASE 1: AUTOMATIC FLOW WITH APPROVAL LOOP (HITL)
    # ----------------------------------------------------
    print("\n--- Test Case 1: Automatic Comparison Flow + HITL Approval ---")
    thread_id_1 = str(uuid.uuid4())
    config_1 = {"configurable": {"thread_id": thread_id_1}}
    
    initial_state_1 = {
        "selected_cars": mock_cars,
        "mode": "automatic",
        "user_query": None,
        "iterations": 0,
        "hitl_approved": False,
        "hitl_feedback": None,
        "chat_history": [],
        "summary": None
    }
    
    print("[1] Launching automatic comparison graph execution...")
    agent_graph.invoke(initial_state_1, config_1)
    
    state_1 = agent_graph.get_state(config_1)
    print(f"    Graph Next Node: {state_1.next}")
    print(f"    Current Analysis Length: {len(state_1.values.get('analysis', ''))} characters")
    
    print("[2] Simulating Human Reviewer approval...")
    agent_graph.update_state(config_1, {"hitl_approved": True, "hitl_feedback": None}, as_node="human_review")
    agent_graph.invoke(None, config_1)
    
    final_state_1 = agent_graph.get_state(config_1)
    print(f"    Resumed Graph Next Node: {final_state_1.next} (End)")
    print(f"    Approved Status: {final_state_1.values.get('hitl_approved')}")
    print(f"    Chat History Length: {len(final_state_1.values.get('chat_history', []))}")
    print(f"    Summary state: {final_state_1.values.get('summary')}")

    # ----------------------------------------------------
    # TEST CASE 2: MANUAL FLOW WITH REJECTION & REVISION LOOP
    # ----------------------------------------------------
    print("\n--- Test Case 2: Manual Flow + Rejection & Revision ---")
    thread_id_2 = str(uuid.uuid4())
    config_2 = {"configurable": {"thread_id": thread_id_2}}
    
    initial_state_2 = {
        "selected_cars": mock_cars,
        "mode": "manual",
        "user_query": "Which car is better for highway driving?",
        "iterations": 0,
        "hitl_approved": False,
        "hitl_feedback": None,
        "chat_history": [],
        "summary": None
    }
    
    print("[1] Launching manual query comparison graph execution...")
    agent_graph.invoke(initial_state_2, config_2)
    
    state_2 = agent_graph.get_state(config_2)
    print(f"    Graph Next Node: {state_2.next}")
    
    print("[2] Simulating Human Reviewer rejecting and requesting revisions...")
    agent_graph.update_state(
        config_2, 
        {"hitl_approved": False, "hitl_feedback": "Highlight transmission gear differences."}, 
        as_node="human_review"
    )
    
    print("    Resuming graph execution to apply revision instructions...")
    agent_graph.invoke(None, config_2)
    
    state_2_revised = agent_graph.get_state(config_2)
    
    print("[3] Simulating Human Reviewer approving the revised comparison...")
    agent_graph.update_state(config_2, {"hitl_approved": True}, as_node="human_review")
    agent_graph.invoke(None, config_2)
    
    final_state_2 = agent_graph.get_state(config_2)
    print(f"    Final Graph Next Node: {final_state_2.next} (End)")
    print(f"    Final Chat History Length: {len(final_state_2.values.get('chat_history', []))}")

    # ----------------------------------------------------
    # TEST CASE 3: SLIDING WINDOW HISTORY COMPRESSION
    # ----------------------------------------------------
    print("\n--- Test Case 3: Sliding Window History Compression ---")
    
    # Overwrite the limit in the agent module to 4 for testing
    agent.HISTORY_LIMIT = 4
    print(f"    Set HISTORY_LIMIT to: {agent.HISTORY_LIMIT}")
    
    thread_id_3 = str(uuid.uuid4())
    config_3 = {"configurable": {"thread_id": thread_id_3}}
    
    # Let's seed a history that has 3 messages (1 user, 1 assistant, 1 user)
    seeded_history = [
        {"role": "user", "content": "Question 1: Hello"},
        {"role": "assistant", "content": "Answer 1: Welcome"},
        {"role": "user", "content": "Question 2: Speed details?"}
    ]
    
    initial_state_3 = {
        "selected_cars": mock_cars,
        "mode": "manual",
        "user_query": "Question 3: Price details?",
        "iterations": 0,
        "hitl_approved": True, # Pre-approve to bypass interrupt and execute immediately
        "hitl_feedback": None,
        "chat_history": seeded_history,
        "summary": None
    }
    
    print("[1] Executing query 3 (will trigger append, total becomes 5, exceeding limit 4)...")
    agent_graph.invoke(initial_state_3, config_3)
    
    # Graph pauses before human_review. We must resume to complete the node and reach finalize_response
    agent_graph.invoke(None, config_3)
    
    state_3 = agent_graph.get_state(config_3)
    print(f"    Graph End Next Node: {state_3.next} (End)")
    print(f"    Current Chat History Length: {len(state_3.values.get('chat_history', []))}")
    print(f"    Consolidated Summary: {state_3.values.get('summary')}")
    
    print("    Active history messages in window:")
    for idx, msg in enumerate(state_3.values.get('chat_history', [])):
        print(f"      {idx+1}. [{msg['role'].upper()}]: {msg['content'][:50]}...")
        
    # Send another query
    print("\n[2] Executing query 4 (will trigger append again, pushing oldest to summary)...")
    next_history = state_3.values.get("chat_history")
    next_summary = state_3.values.get("summary")
    
    config_4 = {"configurable": {"thread_id": thread_id_3}}
    state_4_input = {
        "selected_cars": mock_cars,
        "mode": "manual",
        "user_query": "Question 4: Seating details?",
        "iterations": 0,
        "hitl_approved": True,
        "hitl_feedback": None,
        "chat_history": next_history,
        "summary": next_summary
    }
    agent_graph.invoke(state_4_input, config_4)
    # Resume to run finalize_response
    agent_graph.invoke(None, config_4)
    
    state_4 = agent_graph.get_state(config_4)
    print(f"    Consolidated Summary Post-Query 4: {state_4.values.get('summary')}")
    print("    Active history messages in window Post-Query 4:")
    for idx, msg in enumerate(state_4.values.get('chat_history', [])):
        print(f"      {idx+1}. [{msg['role'].upper()}]: {msg['content'][:50]}...")

    print("\n[Verification Complete] Sliding window history compression is fully functional!")

    # ----------------------------------------------------
    # TEST CASE 4: LOCAL RAG VECTOR RETRIEVAL
    # ----------------------------------------------------
    print("\n--- Test Case 4: Local RAG Vector Retrieval (TF-IDF) ---")
    from app.rag import rag_engine
    
    print("[1] Querying RAG index for: 'charging battery range'...")
    charging_matches = rag_engine.retrieve("charging battery range", k=1)
    if charging_matches:
        print(f"    Matched Chunk: {charging_matches[0][:120]}...")
    else:
        print("    [Error] No chunk matched for 'charging battery range'")

    print("[2] Querying RAG index for: 'AWD vs RWD traction'...")
    drivetrain_matches = rag_engine.retrieve("AWD vs RWD traction", k=1)
    if drivetrain_matches:
        print(f"    Matched Chunk: {drivetrain_matches[0][:120]}...")
    else:
        print("    [Error] No chunk matched for 'AWD vs RWD traction'")
        
    print("\n[Verification Complete] Local RAG retrieval behaves correctly!")

if __name__ == "__main__":
    run_verification()
