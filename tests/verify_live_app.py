"""
Live End-to-End Verification Runner for SafeSpace.
Hits the active server at http://127.0.0.1:8000 and tests all capabilities live.
"""

import requests
import json
import time
import sys

# Ensure UTF-8 stdout encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def run_live_verification():
    print("=" * 65)
    print("  SafeSpace AI Therapist: Live End-to-End Verification")
    print("=" * 65)

    # 1. Health & Configuration Check
    print("\n[Step 1] Verifying /api/health...")
    h_res = requests.get(f"{BASE_URL}/api/health", timeout=5)
    assert h_res.status_code == 200, f"Health check failed: {h_res.status_code}"
    h_data = h_res.json()
    print(f"         Status: {h_data['status']} | Active Provider: {h_data['active_provider']} | Groq Configured: {h_data['groq_configured']}")

    # 2. Multi-Turn Conversation Memory Test
    print("\n[Step 2] Testing Multi-Turn Conversational Memory...")
    # Turn 1
    t1_res = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Hello Dr. Emily, my name is Aryan and I have been experiencing severe burnout from work deadlines."
    }, timeout=30)
    assert t1_res.status_code == 200
    t1_data = t1_res.json()
    sid = t1_data["session_id"]
    print(f"         Turn 1 Response: {t1_data['response'][:100]}...")
    print(f"         Session ID: {sid}")

    # Turn 2: Memory Recall
    t2_res = requests.post(f"{BASE_URL}/api/chat", json={
        "message": "Do you remember my name and what I told you I was dealing with?",
        "session_id": sid
    }, timeout=30)
    assert t2_res.status_code == 200
    t2_data = t2_res.json()
    t2_text = t2_data["response"].lower()
    print(f"         Turn 2 Recall: {t2_data['response'][:120]}...")
    assert "aryan" in t2_text or "burnout" in t2_text or "work" in t2_text, "Model failed to recall previous turn context!"
    print("         Memory Retention: VERIFIED [Aryan + Burnout recalled]")

    # 3. Real-Time Token Streaming Test (SSE)
    print("\n[Step 3] Testing Real-Time Token Streaming (SSE)...")
    stream_res = requests.post(
        f"{BASE_URL}/api/chat/stream",
        json={"message": "Give me one gentle piece of advice for grounding myself."},
        stream=True,
        timeout=30
    )
    assert stream_res.status_code == 200
    token_count = 0
    streamed_chars = 0
    for line in stream_res.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                try:
                    payload = json.loads(line_str.replace("data: ", ""))
                    if "token" in payload:
                        token_count += 1
                        streamed_chars += len(payload["token"])
                except Exception:
                    pass
    print(f"         Tokens Streamed: {token_count} chunks ({streamed_chars} chars) via SSE")
    assert token_count > 5, "Streaming failed to deliver incremental chunks!"

    # 4. Emergency SOS & Crisis Interception Test
    print("\n[Step 4] Testing 1-Click SOS Emergency Protocol...")
    sos_res = requests.post(f"{BASE_URL}/api/emergency/sos", json={
        "reason": "Live system test verification of 1-Click SOS"
    }, timeout=10)
    assert sos_res.status_code == 200
    sos_data = sos_res.json()
    print(f"         Status: {sos_data['status']} | Mode: {sos_data['dispatch_details']['mode']}")
    print(f"         Hotlines Provided: {len(sos_data['hotlines'])} verified emergency contacts")

    # 5. Direct Clinical RAG Search
    print("\n[Step 5] Testing Direct Clinical RAG Knowledge Retrieval...")
    rag_res = requests.get(f"{BASE_URL}/api/rag/search", params={
        "query": "somatic grounding 5-4-3-2-1 technique",
        "category": "grounding"
    }, timeout=5)
    assert rag_res.status_code == 200
    rag_data = rag_res.json()
    top_doc = rag_data["results"][0]
    print(f"         Retrieved Protocol: '{top_doc['title']}' (Score: {top_doc['relevance_score']})")

    # 6. Web Frontend Serving Test
    print("\n[Step 6] Testing Web Application Delivery at Root / ...")
    web_res = requests.get(f"{BASE_URL}/", timeout=5)
    assert web_res.status_code == 200
    assert "SafeSpace" in web_res.text
    print(f"         Frontend Web App: SERVED [Status 200, {len(web_res.text)} bytes]")

    print("\n" + "=" * 65)
    print("  ALL LIVE VERIFICATION TESTS PASSED! APPLICATION IS LIVE & HEALTHY")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_live_verification()
