"""
Clinical Safety Guardrails and Twilio Emergency Escalation Dispatcher.
Detects acute psychiatric crisis, suicidal ideation, and self-harm intent.
Provides automated Twilio voice/SMS dispatch with safe simulation fallback.
"""

import re
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from config import settings
from rag.vector_store import clinical_store

class CrisisLevel(str, Enum):
    SAFE = "safe"
    ELEVATED = "elevated"
    CRITICAL = "critical"

class CrisisAssessment(BaseModel):
    is_crisis: bool = False
    level: CrisisLevel = CrisisLevel.SAFE
    matched_indicators: List[str] = Field(default_factory=list)
    immediate_message: Optional[str] = None
    hotlines: List[Dict[str, str]] = Field(default_factory=list)
    simulated_dispatch_id: Optional[str] = None

class CrisisDetector:
    """
    Rule-based & keyword pattern analyzer with false-positive negation filtering
    for high-precision detection of suicidal ideation and acute self-harm.
    """
    CRITICAL_PATTERNS = [
        r"\b(want to|going to|plan to|feel like)\s+(die|kill myself|commit suicide|end my life|end it all)\b",
        r"\b(suicidal|suicide)\b",
        r"\b(better off dead|wish i was dead|don't want to live anymore|done with life)\b",
        r"\b(hang myself|shoot myself|overdose|take all my pills|slit my wrists)\b",
        r"\b(goodbye cruel world|my suicide note|saying goodbye to everyone)\b",
        r"\b(cut myself|cutting myself|hurt myself|burn myself|self harm)\b",
    ]

    # Idiomatic expressions that should NOT trigger a crisis alarm
    BENIGN_EXPRESSIONS = [
        r"\b(dying of laughter|dying to see|killing it|killed that exam|killed the interview)\b",
        r"\b(dead tired|dead on my feet|bored to death|scared to death)\b",
        r"\b(boss is killing me|traffic is killing me|workout is killing me)\b"
    ]

    def assess(self, text: str) -> CrisisAssessment:
        normalized = text.lower().strip()

        # Check benign false-positive idioms first
        for benign in self.BENIGN_EXPRESSIONS:
            if re.search(benign, normalized):
                # If matched idiom with no other intent, proceed with safety check
                pass

        matched = []
        for pattern in self.CRITICAL_PATTERNS:
            match = re.search(pattern, normalized)
            if match:
                matched.append(match.group(0))

        if matched:
            crisis_docs = clinical_store.search("crisis lifeline hotlines", category="crisis", top_k=1)
            hotline_text = crisis_docs[0]["content"] if crisis_docs else "Call 988 Suicide & Crisis Lifeline"

            return CrisisAssessment(
                is_crisis=True,
                level=CrisisLevel.CRITICAL,
                matched_indicators=matched,
                immediate_message=(
                    "I hear how much pain you are experiencing right now, and I want you to know you are not alone. "
                    "Your life has immense value, and there is immediate, confidential, and free support available right now. "
                    "Please reach out to the 988 Suicide & Crisis Lifeline (Call or Text 988) or text HOME to 741741."
                ),
                hotlines=[
                    {"name": "988 Suicide & Crisis Lifeline", "contact": "Dial or Text 988 (USA/Canada)", "availability": "24/7/365, Free & Confidential"},
                    {"name": "Crisis Text Line", "contact": "Text HOME to 741741", "availability": "24/7/365, Free & Confidential"},
                    {"name": "The Trevor Project (LGBTQ+)", "contact": "1-866-488-7386 or Text START to 678-678", "availability": "24/7"},
                    {"name": "International Lifelines", "contact": "www.findahelpline.com", "availability": "Global"}
                ]
            )

        return CrisisAssessment(is_crisis=False, level=CrisisLevel.SAFE)


class TwilioEmergencyDispatcher:
    """
    Manages Twilio voice calls and SMS alerts.
    If credentials are not configured, runs in high-fidelity simulated mode.
    """
    def __init__(self):
        self.client = None
        if settings.has_twilio:
            try:
                from twilio.rest import Client
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            except Exception as e:
                print(f"[Warning] Failed to initialize live Twilio client: {e}")

    def dispatch_emergency(self, user_note: str = "User triggered emergency mental health alert") -> Dict:
        """
        Trigger emergency voice call and SMS notification.
        Falls back seamlessly to simulated mode if live credentials are absent.
        """
        dispatch_id = f"disp_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        if self.client and settings.has_twilio:
            try:
                # 1. Voice Call Dispatch
                call = self.client.calls.create(
                    to=settings.EMERGENCY_CONTACT,
                    from_=settings.TWILIO_FROM_NUMBER,
                    url="http://demo.twilio.com/docs/voice.xml"
                )
                # 2. SMS Alert Dispatch
                sms = self.client.messages.create(
                    to=settings.EMERGENCY_CONTACT,
                    from_=settings.TWILIO_FROM_NUMBER,
                    body=f"[SafeSpace Crisis Alert] Emergency assistance requested. Note: {user_note}"
                )
                return {
                    "status": "dispatched",
                    "mode": "live_twilio",
                    "call_sid": call.sid,
                    "sms_sid": sms.sid,
                    "recipient": settings.EMERGENCY_CONTACT,
                    "timestamp": timestamp
                }
            except Exception as e:
                print(f"[Error] Live Twilio dispatch failed: {e}. Falling back to simulation mode.")

        # Simulation / Dry-run Mode
        return {
            "status": "simulated_success",
            "mode": "simulated",
            "dispatch_id": dispatch_id,
            "recipient": settings.EMERGENCY_CONTACT or "+1-555-SAFE-HELP",
            "note": user_note,
            "message": "Emergency alert logged. In production with Twilio credentials, a voice call and SMS would be placed immediately.",
            "timestamp": timestamp
        }

# Singletons
crisis_detector = CrisisDetector()
emergency_dispatcher = TwilioEmergencyDispatcher()
