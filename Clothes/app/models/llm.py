import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "CRITICAL ERROR: GROQ_API_KEY is not defined in environment variables or .env file. "
        "Please provide a valid Groq API key."
    )

# Standard model for plain text string output (not versatile)
llm_text = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    groq_api_key=GROQ_API_KEY
)

# Versatile model ONLY used for structured output definitions
llm_structured = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    groq_api_key=GROQ_API_KEY
)
