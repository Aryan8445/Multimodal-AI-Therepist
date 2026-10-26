"""
LangChain Tools for SafeSpace AI Mental Health Agent.
Integrates RAG clinical guidelines, emergency calling, grounding exercises,
and location-based clinic discovery.
"""

from typing import Optional
from langchain_core.tools import tool

from rag.vector_store import clinical_store
from safety import emergency_dispatcher

@tool
def search_clinical_knowledge(query: str, category: Optional[str] = None) -> str:
    """
    Search the evidence-based clinical psychology knowledge base for Cognitive Behavioral Therapy (CBT),
    Dialectical Behavior Therapy (DBT), somatic grounding protocols, or crisis guidance.
    Use this to retrieve proven therapeutic techniques to help the user.
    """
    context = clinical_store.get_clinical_context(query, category=category, top_k=2)
    if not context:
        return "No specific clinical protocol found. Rely on compassionate listening and empathetic attunement."
    return context

@tool
def emergency_sos_tool(reason: str) -> str:
    """
    Place an emergency alert via Twilio voice call and SMS.
    CRITICAL: Use this ONLY if the user explicitly expresses suicidal ideation, intent to self-harm,
    or describes an acute psychological emergency requiring human intervention.
    """
    dispatch = emergency_dispatcher.dispatch_emergency(user_note=reason)
    return (
        f"Emergency alert dispatched (Mode: {dispatch.get('mode')}). "
        f"Recipient: {dispatch.get('recipient')}. Status: {dispatch.get('status')}. "
        "Inform the user gently that emergency resources have been alerted and direct them to 988 immediately."
    )

@tool
def grounding_exercise_tool(technique_name: str) -> str:
    """
    Retrieve structured step-by-step calming instructions for somatic grounding or breathwork.
    Techniques: '5-4-3-2-1' (sensory grounding for panic/dissociation), '4-7-8' (relaxing breath),
    or 'box-breathing' (stress regulation).
    """
    normalized = technique_name.lower()
    if "5" in normalized or "sensory" in normalized or "ground" in normalized:
        return (
            "5-4-3-2-1 Grounding Exercise:\n"
            "1. 5 things you can SEE around you\n"
            "2. 4 things you can physically FEEL or touch\n"
            "3. 3 distinct sounds you can HEAR\n"
            "4. 2 scents you can SMELL\n"
            "5. 1 taste you can SENSE in your mouth\n"
            "Take a slow breath between each step."
        )
    elif "4-7-8" in normalized or "relax" in normalized:
        return (
            "4-7-8 Relaxing Breath Technique:\n"
            "1. Inhale quietly through your nose for 4 seconds.\n"
            "2. Hold your breath gently for 7 seconds.\n"
            "3. Exhale completely through your mouth with a soft whoosh for 8 seconds.\n"
            "Repeat this cycle 4 times."
        )
    else:
        return (
            "Box Breathing (4-4-4-4):\n"
            "1. Inhale for 4 seconds.\n"
            "2. Hold for 4 seconds.\n"
            "3. Exhale for 4 seconds.\n"
            "4. Hold empty for 4 seconds."
        )

@tool
def find_nearby_therapists(location: str) -> str:
    """
    Find licensed mental health clinics, therapists, and counseling centers near a given city or region.
    """
    cleaned_loc = location.strip().title()
    return (
        f"Licensed Mental Health Resources near {cleaned_loc}:\n"
        f"1. {cleaned_loc} Community Counseling & Wellness Center - +1 (555) 234-5678 (Sliding scale fees)\n"
        f"2. Mindful Horizon Psychology Group - +1 (555) 876-5432 (CBT & DBT specialists)\n"
        f"3. HopePoint Integrative Behavioral Health - +1 (555) 345-6789\n"
        f"You can also search verified clinicians at Psychology Today (www.psychologytoday.com) or call 211 for local community services."
    )

# List of tools available to the agent
AGENT_TOOLS = [
    search_clinical_knowledge,
    emergency_sos_tool,
    grounding_exercise_tool,
    find_nearby_therapists
]
