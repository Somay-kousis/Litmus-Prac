import pytest
from app.models.llm import llm_text, llm_structured
from app.prompts.templates import GUARDRAIL_INSTRUCTIONS, DAILY_SUGGESTIONS_SYSTEM

def test_llm_loading():
    assert llm_text is not None
    assert llm_structured is not None
    assert llm_text.model_name == "llama-3.1-8b-instant"
    assert llm_structured.model_name == "llama-3.3-70b-versatile"

def test_prompt_formatting():
    formatted_prompt = DAILY_SUGGESTIONS_SYSTEM.format(guardrail_instructions=GUARDRAIL_INSTRUCTIONS)
    assert "GUARDRAIL RULES:" in formatted_prompt
    assert "prices" in formatted_prompt

def test_llm_connection():
    # Make a simple, fast API call to verify the Groq key is working and connection is alive.
    response = llm_text.invoke("Say 'connection_ok'")
    content = response.content.strip().lower()
    assert "connection" in content or "ok" in content
