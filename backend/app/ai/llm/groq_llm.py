import os
from functools import lru_cache

from dotenv import load_dotenv
from fastapi import HTTPException, status
from langchain_groq import ChatGroq

load_dotenv()


def _create_llm(model: str) -> ChatGroq:
    """Create LLM instance."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GROQ_API_KEY is not configured",
        )
    
    try:
        groq_temperature = float(os.getenv("GROQ_TEMPERATURE", "0.1"))
        groq_timeout = int(os.getenv("GROQ_TIMEOUT", "30"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid Groq configuration values",
        )
    
    return ChatGroq(
        api_key=groq_api_key,
        model=model,
        temperature=groq_temperature,
        timeout=groq_timeout,
    )


@lru_cache
def get_llm() -> ChatGroq:
    """Get LLM with fallback support."""
    
    # Primary model
    primary = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    
    try:
        return _create_llm(primary)
    except Exception:
        # Fallback 1
        try:
            print(f"⚠️ Primary model failed, trying fallback: llama-3.1-8b-instant")
            return _create_llm("llama-3.1-8b-instant")
        except Exception:
            # Fallback 2
            try:
                print(f"⚠️ Fallback 1 failed, trying fallback: mixtral-8x7b-32768")
                return _create_llm("mixtral-8x7b-32768")
            except Exception:
                # Fallback 3
                print(f"⚠️ All models failed, trying last resort: llama-3.2-3b-preview")
                return _create_llm("llama-3.2-3b-preview")

            