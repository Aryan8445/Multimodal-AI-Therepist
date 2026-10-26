"""
Multi-Provider LLM Factory for SafeSpace.
Supports Groq (cloud ultra-fast LPU), Ollama (local private MedGemma/Llama),
OpenAI fallback, and offline Clinical Simulation.
"""

from typing import Optional
from config import settings

def get_llm(provider: Optional[str] = None):
    """
    Instantiate and return the appropriate LangChain chat model.
    Falls back gracefully if the requested provider is unavailable.
    """
    chosen_provider = (provider or settings.DEFAULT_PROVIDER).lower()

    # 1. Groq Cloud (Recommended & Default)
    if chosen_provider == "groq" and settings.has_groq:
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.GROQ_MODEL,
                temperature=0.3,
                max_tokens=800
            )
        except Exception as e:
            print(f"[Warning] Failed to initialize ChatGroq: {e}. Checking fallback.")

    # 2. Ollama Local
    if chosen_provider == "ollama":
        try:
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=0.3
            )
        except Exception as e:
            print(f"[Warning] Failed to initialize ChatOllama: {e}.")

    # 3. OpenAI Fallback
    if settings.OPENAI_API_KEY:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model="gpt-4o-mini",
                temperature=0.3
            )
        except Exception as e:
            print(f"[Warning] Failed to initialize ChatOpenAI: {e}.")

    # 4. If Groq key exists, always try Groq as primary
    if settings.has_groq:
        from langchain_groq import ChatGroq
        return ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=0.3,
            max_tokens=800
        )

    # 5. Offline Simulation Fallback
    return None
