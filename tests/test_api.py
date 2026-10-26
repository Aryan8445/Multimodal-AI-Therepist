import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from main import app
from agent.memory import session_manager

client = TestClient(app)

def test_health_check_endpoint():
    """Verify health endpoint returns 200 and system metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["groq_configured"] is True
    assert data["clinical_docs_indexed"] >= 8

def test_chat_endpoint_lifecycle():
    """Verify multi-turn chat endpoint creates session, responds, and persists history."""
    # 1. Send first turn
    res1 = client.post("/api/chat", json={
        "message": "Hello, I am feeling a bit anxious today about my future."
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert "session_id" in data1
    assert len(data1["response"]) > 30
    assert data1["is_crisis"] is False
    sid = data1["session_id"]

    # 2. Check session history
    res_history = client.get(f"/api/sessions/{sid}/history")
    assert res_history.status_code == 200
    history_data = res_history.json()
    assert len(history_data["messages"]) >= 2

    # 3. List sessions
    res_list = client.get("/api/sessions")
    assert res_list.status_code == 200
    sessions = res_list.json()["sessions"]
    assert any(s["session_id"] == sid for s in sessions)

    # 4. Clean up
    del_res = client.delete(f"/api/sessions/{sid}")
    assert del_res.status_code == 200

def test_chat_stream_endpoint():
    """Verify SSE streaming endpoint returns text/event-stream chunks."""
    with client.stream("POST", "/api/chat/stream", json={"message": "Give me a 1-sentence calming thought."}) as res:
        assert res.status_code == 200
        assert "text/event-stream" in res.headers["content-type"]
        chunks = []
        for line in res.iter_lines():
            if line:
                chunks.append(line)
                if len(chunks) > 3:
                    break
        assert len(chunks) > 0

def test_emergency_sos_endpoint():
    """Verify 1-click SOS endpoint triggers emergency response and returns hotlines."""
    res = client.post("/api/emergency/sos", json={"reason": "Testing emergency 1-click SOS button"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "alert_triggered"
    assert "dispatch_details" in data
    assert len(data["hotlines"]) >= 3

def test_rag_search_endpoint():
    """Verify direct RAG vector search endpoint returns matching clinical protocols."""
    res = client.get("/api/rag/search", params={"query": "TIPP distress tolerance", "category": "dbt"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) > 0
    assert "TIPP" in data["results"][0]["content"]

def test_legacy_ask_endpoint():
    """Verify backwards compatibility with original /ask route."""
    res = client.post("/ask", json={"message": "I feel stressed"})
    assert res.status_code == 200
    data = res.json()
    assert "response" in data
    assert "tool_called" in data
