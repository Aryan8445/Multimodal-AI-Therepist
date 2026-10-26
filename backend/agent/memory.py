"""
Multi-turn Conversation Session Memory Manager for SafeSpace.
Maintains isolated state, message history, and timestamps across user interactions.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

class SessionManager:
    """
    Manages conversational histories across concurrent user sessions.
    Thread-safe dictionary store for multi-turn conversational agents.
    """
    def __init__(self):
        self._sessions: Dict[str, List[Dict]] = {}
        self._metadata: Dict[str, Dict] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        if not session_id or session_id not in self._sessions:
            sid = session_id or f"sess_{uuid.uuid4().hex[:12]}"
            self._sessions[sid] = []
            self._metadata[sid] = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "title": "New Conversation",
                "message_count": 0
            }
            return sid
        return session_id

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_called: Optional[str] = None
    ):
        sid = self.get_or_create_session(session_id)
        msg = {
            "role": role,
            "content": content,
            "tool_called": tool_called,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._sessions[sid].append(msg)
        self._metadata[sid]["message_count"] = len(self._sessions[sid])

        # Generate automatic title from first user message
        if role == "user" and self._metadata[sid]["title"] == "New Conversation":
            words = content.strip().split()
            title = " ".join(words[:5]) + ("..." if len(words) > 5 else "")
            self._metadata[sid]["title"] = title

    def get_history(self, session_id: str) -> List[Dict]:
        return self._sessions.get(session_id, [])

    def get_formatted_langchain_messages(self, session_id: str) -> List[tuple]:
        """Convert session history into (role, content) tuples for LangChain."""
        history = self.get_history(session_id)
        formatted = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "assistant"
            formatted.append((role, msg["content"]))
        return formatted

    def list_sessions(self) -> List[Dict]:
        results = []
        for sid, meta in self._metadata.items():
            results.append({
                "session_id": sid,
                "title": meta.get("title", "Conversation"),
                "created_at": meta.get("created_at"),
                "message_count": meta.get("message_count", 0)
            })
        return sorted(results, key=lambda x: x["created_at"], reverse=True)

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            if session_id in self._metadata:
                del self._metadata[session_id]
            return True
        return False

# Global Session Manager Singleton
session_manager = SessionManager()
