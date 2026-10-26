import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from config import settings

def test_settings_load():
    """Verify settings loads properly from .env"""
    assert settings.GROQ_MODEL in ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]
    assert settings.DEFAULT_PROVIDER in ["groq", "ollama", "openai", "simulation"]
    assert settings.BACKEND_PORT == 8000

def test_groq_key_presence():
    """Verify Groq API key is populated and starts with gsk_"""
    assert settings.has_groq is True
    assert settings.GROQ_API_KEY.startswith("gsk_")

def test_twilio_graceful_fallback():
    """Verify Twilio has_twilio returns boolean without crashing"""
    assert isinstance(settings.has_twilio, bool)
