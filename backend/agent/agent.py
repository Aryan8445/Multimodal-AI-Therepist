"""
SafeSpace AI Therapist Agent Orchestrator.
Combines Dr. Emily Hartman clinical persona, safety interception,
RAG retrieval, multi-turn memory, and token streaming via Groq.
"""

from typing import AsyncGenerator, Dict, Optional, Tuple
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from agent.llm_provider import get_llm
from agent.tools import AGENT_TOOLS
from agent.memory import session_manager
from safety import crisis_detector, emergency_dispatcher, CrisisAssessment
from rag.vector_store import clinical_store

SYSTEM_PROMPT = """You are Dr. Emily Hartman, a deeply compassionate, warm, and experienced clinical psychologist specializing in Cognitive Behavioral Therapy (CBT) and Dialectical Behavior Therapy (DBT).

Your Core Clinical Principles:
1. Empathetic Attunement: Always start by warmly validating the user's emotions ("I hear how exhausting and overwhelming this has been for you...").
2. Gentle Normalization: Help them understand that their reactions are human and understandable given what they are going through.
3. Evidence-Based Coping: Offer practical, gentle coping techniques (e.g., CBT thought reframing, 5-4-3-2-1 grounding, box breathing, behavioral activation).
4. Socratic Open-Ended Inquiry: Conclude your responses with a gentle, curious question to invite deeper reflection.
5. Absolute Safety: You NEVER prescribe medication or offer medical diagnosis. If you detect acute suicidal ideation or self-harm, immediately express care and direct the user to the 988 Suicide & Crisis Lifeline.

Guidelines:
- Maintain a warm, calm, soothing tone.
- Avoid robotic or clinical jargon; speak like a caring human therapist sitting right in front of them.
- Keep paragraphs readable and concise.
"""

class TherapistAgent:
    def __init__(self):
        self.llm = get_llm()

    def _fallback_simulation_response(self, user_message: str, rag_context: str = "") -> str:
        """Intelligent clinical simulation engine when no LLM API is reachable."""
        msg = user_message.lower()
        if "panic" in msg or "anxious" in msg or "overwhelm" in msg:
            return (
                "I can sense how overwhelming this feeling is right now, and I want to remind you that you are safe in this moment. "
                "When anxiety surges, our bodies activate the fight-or-flight response. Let's try the 5-4-3-2-1 grounding exercise together:\n\n"
                "Can you take a slow breath, look around your room, and notice 5 things you can see right now? "
                "Tell me what they are, and we will take this one gentle step at a time."
            )
        elif "sad" in msg or "depress" in msg or "hopeless" in msg or "tired" in msg:
            return (
                "Thank you for sharing this with me. Carrying that weight can feel so exhausting, and I hear how heavy things feel today. "
                "It takes real courage to put these feelings into words. When energy is low, even small things count as victories.\n\n"
                "If it feels okay to explore, how long have you been carrying this heaviness, and what is one gentle thing you might need right now?"
            )
        else:
            return (
                "I am here with you, listening closely to everything you're sharing. "
                "Your feelings are completely valid, and whatever you are experiencing is worthy of care and attention.\n\n"
                "Could you tell me a little more about what triggered this feeling today?"
            )

    async def process_message(
        self,
        session_id: str,
        user_message: str,
        provider: Optional[str] = None
    ) -> Dict:
        """
        Non-streaming message processor.
        Returns response text, safety assessment, tool called, and citations.
        """
        sid = session_manager.get_or_create_session(session_id)

        # 1. Run Safety Guardrail
        assessment = crisis_detector.assess(user_message)
        if assessment.is_crisis:
            # Emergency Intervention Escalation
            dispatch = emergency_dispatcher.dispatch_emergency(f"Crisis detected: {user_message[:100]}")
            response_text = (
                f"{assessment.immediate_message}\n\n"
                f"**Emergency Resources Available Right Now:**\n"
                f"- **988 Suicide & Crisis Lifeline**: Call or text 988 (Available 24/7, Free, Confidential)\n"
                f"- **Crisis Text Line**: Text HOME to 741741\n"
                f"- **The Trevor Project**: 1-866-488-7386\n"
                f"- **International Directory**: [findahelpline.com](https://findahelpline.com)\n\n"
                f"*SafeSpace has automatically logged an emergency safety alert ({dispatch.get('status')}). Please connect with one of these lifelines immediately.*"
            )
            session_manager.add_message(sid, "user", user_message)
            session_manager.add_message(sid, "assistant", response_text, tool_called="emergency_sos_tool")
            return {
                "session_id": sid,
                "response": response_text,
                "is_crisis": True,
                "tool_called": "emergency_sos_tool",
                "citations": ["988 Suicide & Crisis Lifeline", "Crisis Text Line"]
            }

        # 2. Record User Message
        session_manager.add_message(sid, "user", user_message)

        # 3. Retrieve relevant clinical RAG context
        rag_context = clinical_store.get_clinical_context(user_message, top_k=2)

        # 4. Prepare prompt with memory history
        history = session_manager.get_formatted_langchain_messages(sid)
        llm = get_llm(provider) or self.llm

        if not llm:
            # Offline Simulation
            sim_response = self._fallback_simulation_response(user_message, rag_context)
            session_manager.add_message(sid, "assistant", sim_response, tool_called="clinical_simulation")
            return {
                "session_id": sid,
                "response": sim_response,
                "is_crisis": False,
                "tool_called": "clinical_simulation",
                "citations": ["Clinical Psychology Knowledge Base"] if rag_context else []
            }

        # Build message history for LangChain
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        if rag_context:
            messages.append(SystemMessage(content=f"Clinical Evidence-Based Protocols for reference:\n{rag_context}"))

        # Add last 6 turns of conversation history
        for role, text in history[-6:]:
            if role == "user":
                messages.append(HumanMessage(content=text))
            else:
                messages.append(AIMessage(content=text))

        try:
            ai_msg = await llm.ainvoke(messages)
            response_text = ai_msg.content
        except Exception as e:
            print(f"[Error in LLM invoke]: {e}. Falling back to simulation.")
            response_text = self._fallback_simulation_response(user_message, rag_context)

        # 5. Save assistant response to memory
        session_manager.add_message(sid, "assistant", response_text, tool_called="search_clinical_knowledge" if rag_context else "None")

        return {
            "session_id": sid,
            "response": response_text,
            "is_crisis": False,
            "tool_called": "search_clinical_knowledge" if rag_context else "None",
            "citations": ["CBT/DBT Protocols"] if rag_context else []
        }

    async def stream_message(
        self,
        session_id: str,
        user_message: str,
        provider: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streaming token generator for Server-Sent Events (SSE).
        Yields tokens in real-time as Groq produces them.
        """
        sid = session_manager.get_or_create_session(session_id)

        # 1. Crisis Check
        assessment = crisis_detector.assess(user_message)
        if assessment.is_crisis:
            dispatch = emergency_dispatcher.dispatch_emergency(f"Crisis detected: {user_message[:100]}")
            alert = (
                f"{assessment.immediate_message}\n\n"
                f"**Emergency Resources Available Right Now:**\n"
                f"- **988 Suicide & Crisis Lifeline**: Call or text 988 (Available 24/7, Free, Confidential)\n"
                f"- **Crisis Text Line**: Text HOME to 741741\n"
                f"- **International Directory**: [findahelpline.com](https://findahelpline.com)\n\n"
                f"*(Emergency safety alert logged: {dispatch.get('status')})*"
            )
            session_manager.add_message(sid, "user", user_message)
            session_manager.add_message(sid, "assistant", alert, tool_called="emergency_sos_tool")
            for token in alert.split(" "):
                yield f"{token} "
            return

        session_manager.add_message(sid, "user", user_message)
        rag_context = clinical_store.get_clinical_context(user_message, top_k=2)
        history = session_manager.get_formatted_langchain_messages(sid)

        llm = get_llm(provider) or self.llm
        if not llm:
            sim = self._fallback_simulation_response(user_message, rag_context)
            session_manager.add_message(sid, "assistant", sim, tool_called="clinical_simulation")
            for token in sim.split(" "):
                yield f"{token} "
            return

        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        if rag_context:
            messages.append(SystemMessage(content=f"Clinical Evidence-Based Protocols for reference:\n{rag_context}"))

        for role, text in history[-6:]:
            if role == "user":
                messages.append(HumanMessage(content=text))
            else:
                messages.append(AIMessage(content=text))

        full_content = []
        try:
            async for chunk in llm.astream(messages):
                token = chunk.content
                if token:
                    full_content.append(token)
                    yield token
        except Exception as e:
            fallback = self._fallback_simulation_response(user_message, rag_context)
            for token in fallback.split(" "):
                yield f"{token} "
            full_content.append(fallback)

        complete_response = "".join(full_content)
        session_manager.add_message(sid, "assistant", complete_response)

# Agent Singleton
therapist_agent = TherapistAgent()
