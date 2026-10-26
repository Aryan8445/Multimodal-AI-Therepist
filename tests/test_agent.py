import sys
from pathlib import Path
import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from agent.llm_provider import get_llm
from agent.memory import session_manager
from agent.tools import (
    search_clinical_knowledge,
    grounding_exercise_tool,
    emergency_sos_tool,
    find_nearby_therapists
)
from agent.agent import therapist_agent

def test_llm_groq_instantiation():
    """Verify Groq LLM can be instantiated successfully."""
    llm = get_llm("groq")
    assert llm is not None
    assert llm.model_name in ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]

def test_session_memory_lifecycle():
    """Verify multi-turn session creation, messages, and deletion."""
    sid = session_manager.get_or_create_session("agent_test_sess")
    session_manager.add_message(sid, "user", "I'm having anxiety about my job")
    session_manager.add_message(sid, "assistant", "I hear you, work anxiety is very challenging.")

    history = session_manager.get_history(sid)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

    # Cleanup
    assert session_manager.delete_session(sid) is True

def test_agent_tools():
    """Verify each LangChain tool can be invoked and returns string output."""
    res_rag = search_clinical_knowledge.invoke({"query": "cognitive distortions catastrophizing"})
    assert isinstance(res_rag, str)
    assert len(res_rag) > 20

    res_grounding = grounding_exercise_tool.invoke({"technique_name": "5-4-3-2-1"})
    assert "SEE" in res_grounding
    assert "FEEL" in res_grounding

    res_clinics = find_nearby_therapists.invoke({"location": "San Francisco"})
    assert "San Francisco" in res_clinics

    res_sos = emergency_sos_tool.invoke({"reason": "Test emergency call"})
    assert "Emergency alert dispatched" in res_sos

@pytest.mark.asyncio
async def test_agent_live_groq_response():
    """Integration: Test real live Groq API inference through the agent."""
    sid = "live_test_session"
    res = await therapist_agent.process_message(
        session_id=sid,
        user_message="Hello Dr. Emily, I've been feeling stressed and overwhelmed with deadlines."
    )

    assert res["session_id"] == sid
    assert res["is_crisis"] is False
    assert len(res["response"]) > 50
    # Clean up
    session_manager.delete_session(sid)

@pytest.mark.asyncio
async def test_agent_crisis_interception():
    """Integration: Verify agent halts and triggers crisis safety protocol on suicidal ideation."""
    sid = "crisis_test_session"
    res = await therapist_agent.process_message(
        session_id=sid,
        user_message="I want to kill myself tonight, please help."
    )

    assert res["is_crisis"] is True
    assert res["tool_called"] == "emergency_sos_tool"
    assert "988" in res["response"]
    # Clean up
    session_manager.delete_session(sid)

@pytest.mark.asyncio
async def test_agent_streaming():
    """Integration: Test real-time token streaming generator."""
    sid = "stream_test_session"
    tokens = []
    async for token in therapist_agent.stream_message(sid, "Tell me what 4-7-8 breathing is in one sentence"):
        tokens.append(token)

    assert len(tokens) > 5
    full_text = "".join(tokens)
    assert len(full_text) > 20
    session_manager.delete_session(sid)
