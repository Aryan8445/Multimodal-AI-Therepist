"""
Scalable FastAPI Backend for SafeSpace AI Mental Health Therapist.
Provides multi-turn session persistence, SSE token streaming,
emergency SOS dispatch, and clinical RAG exploration.
"""

import json
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from agent.agent import therapist_agent
from agent.memory import session_manager
from safety import emergency_dispatcher
from rag.vector_store import clinical_store

# Initialize FastAPI App
app = FastAPI(
    title="SafeSpace AI Therapist API",
    description="Scalable, empathetic mental health agent backend with RAG, Groq LLMs, and emergency escalation.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Request & Response Schemas
# ---------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's message or emotional question")
    session_id: Optional[str] = Field(default=None, description="Conversation session ID for multi-turn history")
    provider: Optional[str] = Field(default=None, description="LLM provider: groq, ollama, simulation")

class ChatResponse(BaseModel):
    session_id: str
    response: str
    is_crisis: bool
    tool_called: str
    citations: List[str]

class EmergencyRequest(BaseModel):
    reason: Optional[str] = Field(default="User initiated 1-click SOS button", description="Context for emergency dispatch")

class LegacyQuery(BaseModel):
    message: str

# ---------------------------------------------------------
# Core API Routes
# ---------------------------------------------------------
@app.get("/api/health")
async def health_check():
    """Health check endpoint displaying system and provider availability."""
    return {
        "status": "healthy",
        "service": "SafeSpace AI Therapist Backend",
        "version": "1.0.0",
        "active_provider": settings.DEFAULT_PROVIDER,
        "groq_configured": settings.has_groq,
        "twilio_configured": settings.has_twilio,
        "clinical_docs_indexed": len(clinical_store.documents)
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Standard multi-turn chat endpoint.
    Maintains conversational memory, applies clinical safety guardrails,
    and returns comprehensive response metadata.
    """
    try:
        result = await therapist_agent.process_message(
            session_id=request.session_id or "",
            user_message=request.message,
            provider=request.provider
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating therapeutic response: {str(e)}"
        )

@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Server-Sent Events (SSE) streaming chat endpoint.
    Streams token-by-token responses from Groq LPU in real-time.
    """
    sid = session_manager.get_or_create_session(request.session_id)

    async def token_generator():
        try:
            async for token in therapist_agent.stream_message(sid, request.message, request.provider):
                data = json.dumps({"session_id": sid, "token": token})
                yield f"data: {data}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            err_data = json.dumps({"error": str(e)})
            yield f"data: {err_data}\n\n"

    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/api/emergency/sos")
async def emergency_sos_endpoint(request: EmergencyRequest):
    """
    Direct 1-Click SOS emergency trigger.
    Places Twilio voice call & SMS notification and returns 988 emergency guidance.
    """
    dispatch = emergency_dispatcher.dispatch_emergency(request.reason or "1-Click SOS triggered")
    return {
        "status": "alert_triggered",
        "dispatch_details": dispatch,
        "hotlines": [
            {"name": "988 Suicide & Crisis Lifeline", "contact": "Call or Text 988", "availability": "24/7/365 Free & Confidential"},
            {"name": "Crisis Text Line", "contact": "Text HOME to 741741", "availability": "24/7/365 Free"},
            {"name": "The Trevor Project", "contact": "1-866-488-7386", "availability": "LGBTQ+ Youth 24/7"}
        ]
    }

@app.get("/api/sessions")
async def list_sessions():
    """Retrieve all active conversation sessions and their metadata."""
    return {"sessions": session_manager.list_sessions()}

@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Retrieve full chat turn history for a given session."""
    history = session_manager.get_history(session_id)
    if not history and session_id not in session_manager._metadata:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": history}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session and free memory."""
    success = session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": True, "session_id": session_id}

@app.get("/api/rag/search")
async def search_rag_knowledge(query: str, category: Optional[str] = None, top_k: int = 3):
    """Direct clinical RAG vector database exploration."""
    results = clinical_store.search(query=query, category=category, top_k=top_k)
    return {"query": query, "results": results}

# Backwards compatibility with original tutorial
@app.post("/ask")
async def ask_legacy(query: LegacyQuery):
    """Legacy endpoint for compatibility with original tutorial scripts."""
    result = await therapist_agent.process_message(
        session_id="legacy_default",
        user_message=query.message
    )
# Serve Frontend Web Application
from pathlib import Path
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
