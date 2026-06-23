import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, model_validator
from app.graph.builder import agent_graph

app = FastAPI(title="AI Clothing Shopping Assistant API")

# Setup CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas with strict input validation to enforce pricing guardrails
class CartItem(BaseModel):
    item_id: str
    name: str
    category: str
    color: str
    size: str

    @model_validator(mode="before")
    @classmethod
    def check_no_pricing_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for k, v in data.items():
                # Check keys
                if any(forbidden in str(k).lower() for forbidden in ["price", "cost", "discount", "sale"]):
                    raise ValueError(f"Input validation error: forbidden pricing parameter '{k}' in cart item.")
                # Check values
                if any(forbidden in str(v).lower() for forbidden in ["$", "usd", "inr", "discount", "sale"]):
                    raise ValueError(f"Input validation error: forbidden pricing term inside value '{v}' in cart item.")
        return data

class SuggestionsRequest(BaseModel):
    cart: List[CartItem] = []
    clicks: List[str] = []
    previous_chats: List[str] = []

class SuggestionsResponse(BaseModel):
    suggestions: List[str]

class ChatRequest(BaseModel):
    user_query: str
    cart: List[CartItem] = []
    clicks: List[str] = []
    previous_chats: List[str] = []
    chat_history: List[Dict[str, str]] = []
    recipient: Optional[str] = "self"
    recipient_profiles: Dict[str, Any] = {}
    summary: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    chat_history: List[Dict[str, str]]
    recipient: str
    recipient_profiles: Dict[str, Any]
    summary: Optional[str] = None

@app.post("/suggestions", response_model=SuggestionsResponse)
def get_daily_suggestions(request: SuggestionsRequest):
    initial_state = {
        "mode": "automated",
        "cart": [item.model_dump() for item in request.cart],
        "clicks": request.clicks,
        "previous_chats": request.previous_chats,
        "chat_history": []
    }
    
    try:
        res = agent_graph.invoke(initial_state)
        return SuggestionsResponse(suggestions=res.get("suggestions", []))
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Graph Execution Error: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
def send_chat_message(request: ChatRequest):
    if not request.user_query.strip():
        raise HTTPException(status_code=400, detail="User query cannot be empty.")

    initial_state = {
        "mode": "manual",
        "user_query": request.user_query,
        "cart": [item.model_dump() for item in request.cart],
        "clicks": request.clicks,
        "previous_chats": request.previous_chats,
        "chat_history": request.chat_history,
        "recipient": request.recipient,
        "recipient_profiles": request.recipient_profiles,
        "summary": request.summary
    }
    
    try:
        res = agent_graph.invoke(initial_state)
        return ChatResponse(
            response=res.get("response", ""),
            chat_history=res.get("chat_history", []),
            recipient=res.get("recipient", "self"),
            recipient_profiles=res.get("recipient_profiles", {}),
            summary=res.get("summary")
        )
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Graph Execution Error: {str(e)}")

# Mount static files folder
static_path = Path(__file__).resolve().parent.parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_file = static_path / "index.html"
    if index_file.exists():
        return index_file.read_text()
    return """
    <html>
        <head><title>AI Styling Assistant</title></head>
        <body style="font-family: sans-serif; background-color: #0b0f19; color: #fff; text-align: center; padding-top: 100px;">
            <h1>AI Styling Assistant API is Live</h1>
            <p>Static index.html not generated yet.</p>
        </body>
    </html>
    """
