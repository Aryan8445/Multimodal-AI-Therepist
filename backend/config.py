from typing import Optional, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Project root directory (parent of backend)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """
    Centralized configuration management for SafeSpace.
    Loads settings from .env file with graceful defaults.
    """
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Groq Cloud Configuration
    GROQ_API_KEY: str = Field(default="", description="Groq API Key (Free tier from console.groq.com)")
    GROQ_MODEL: str = Field(default="openai/gpt-oss-120b", description="Default Groq Model")

    # OpenAI Fallback
    OPENAI_API_KEY: Optional[str] = Field(default="", description="OpenAI API Key for fallback")

    # Ollama Local Configuration
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama endpoint")
    OLLAMA_MODEL: str = Field(default="alibayram/medgemma:4b", description="Ollama model")

    # Active Provider: "groq", "ollama", "openai", "simulation"
    DEFAULT_PROVIDER: Literal["groq", "ollama", "openai", "simulation"] = Field(
        default="groq",
        description="Active LLM Provider"
    )

    # Twilio Emergency Calling & SMS
    TWILIO_ACCOUNT_SID: str = Field(default="", description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(default="", description="Twilio Auth Token")
    TWILIO_FROM_NUMBER: str = Field(default="", description="Twilio Sender Phone Number")
    EMERGENCY_CONTACT: str = Field(default="", description="Emergency recipient phone number")

    # Server Settings
    BACKEND_HOST: str = Field(default="0.0.0.0", description="Backend host binding")
    BACKEND_PORT: int = Field(default=8000, description="Backend port")

    # ChromaDB Vector Store Directory
    CHROMA_PERSIST_DIR: str = Field(
        default=str(BASE_DIR / "chroma_db"),
        description="Path to local ChromaDB vector store"
    )

    @property
    def has_groq(self) -> bool:
        """Check if a valid Groq API key is present."""
        return bool(self.GROQ_API_KEY and self.GROQ_API_KEY.startswith("gsk_"))

    @property
    def has_twilio(self) -> bool:
        """Check if complete Twilio credentials are configured."""
        return bool(
            self.TWILIO_ACCOUNT_SID 
            and self.TWILIO_AUTH_TOKEN 
            and self.TWILIO_FROM_NUMBER 
            and self.EMERGENCY_CONTACT
        )

# Global settings singleton
settings = Settings()