import sys
from pathlib import Path
import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from safety import crisis_detector, emergency_dispatcher, CrisisLevel

def test_safe_messages():
    """Verify benign everyday stress does not trigger crisis."""
    res1 = crisis_detector.assess("I had a very difficult day at work and feel anxious.")
    assert res1.is_crisis is False
    assert res1.level == CrisisLevel.SAFE

    res2 = crisis_detector.assess("I have an exam tomorrow and I'm feeling overwhelmed.")
    assert res2.is_crisis is False
    assert res2.level == CrisisLevel.SAFE

def test_idiomatic_expressions_not_flagged():
    """Verify common non-suicidal idioms are not flagged as crises."""
    res = crisis_detector.assess("That comedy show was hilarious, I was dying of laughter!")
    assert res.is_crisis is False

def test_critical_suicidal_intent_detected():
    """Verify acute suicidal ideation triggers critical crisis state."""
    res = crisis_detector.assess("I can't take this anymore, I want to end my life tonight.")
    assert res.is_crisis is True
    assert res.level == CrisisLevel.CRITICAL
    assert len(res.matched_indicators) > 0
    assert len(res.hotlines) >= 3
    assert any("988" in h["name"] for h in res.hotlines)

def test_self_harm_detected():
    """Verify self-harm intent is caught by safety guardrail."""
    res = crisis_detector.assess("I feel completely numb and I want to cut myself.")
    assert res.is_crisis is True
    assert res.level == CrisisLevel.CRITICAL

def test_emergency_dispatch_simulated():
    """Verify emergency dispatcher safely dispatches in simulated mode."""
    dispatch = emergency_dispatcher.dispatch_emergency("Test user triggered emergency in unit tests")
    assert dispatch["status"] in ["dispatched", "simulated_success"]
    assert "recipient" in dispatch
    assert "timestamp" in dispatch

def test_safety_rag_integration():
    """Integration: Verify crisis assessment attaches 988 lifeline instructions from clinical knowledge."""
    res = crisis_detector.assess("I feel like I want to die")
    assert res.is_crisis is True
    assert res.immediate_message is not None
    assert "988" in res.immediate_message
