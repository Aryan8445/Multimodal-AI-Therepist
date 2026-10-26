import streamlit as st
import requests
import uuid

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="SafeSpace – AI Mental Health Therapist",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #0b1120; }
    .stChatMessage { border-radius: 12px; margin-bottom: 12px; }
    .crisis-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(245, 158, 11, 0.2));
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = f"st_sess_{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar Controls & Toolkit
with st.sidebar:
    st.title("🌿 SafeSpace")
    st.caption("Multimodal AI Therapist • Groq & RAG Guided")

    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.session_id = f"st_sess_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("🚨 Emergency Assistance")
    st.caption("Immediate confidential human support:")
    st.markdown("**📞 Dial 988** (Suicide & Crisis Lifeline)")
    st.markdown("**💬 Text HOME to 741741** (Crisis Text Line)")

    if st.button("🚨 1-Click SOS Alert", type="primary", use_container_width=True):
        try:
            sos_res = requests.post(f"{BACKEND_URL}/api/emergency/sos", json={"reason": "Streamlit 1-Click SOS triggered"})
            st.error("Automated emergency alert dispatched. Please dial 988 immediately.")
        except Exception as e:
            st.warning("Emergency alert simulated. Dial 988 immediately.")

    st.divider()

    st.subheader("🧘 Therapeutic Tools")
    tool_choice = st.selectbox(
        "Select Quick Coping Exercise:",
        ["None", "4-7-8 Breathing Pacer", "5-4-3-2-1 Sensory Grounding", "CBT Thought Reframer"]
    )

    if tool_choice == "4-7-8 Breathing Pacer":
        st.info("🌬️ **Inhale (4s)** $\\rightarrow$ **Hold (7s)** $\\rightarrow$ **Exhale (8s)**. Repeat 4 times to stimulate vagus nerve calming.")
    elif tool_choice == "5-4-3-2-1 Sensory Grounding":
        st.info("👀 5 Things you SEE\n✋ 4 Things you FEEL\n👂 3 Things you HEAR\n👃 2 Things you SMELL\n👅 1 Thing you TASTE")
    elif tool_choice == "CBT Thought Reframer":
        st.info("Identify the automatic negative thought $\\rightarrow$ spot the cognitive distortion $\\rightarrow$ write an evidence-based reframe.")

# Main Chat View
st.title("🧠 SafeSpace – Dr. Emily Hartman")
st.caption("Compassionate, clinical guidance powered by Groq LPU inference, evidence-based CBT/DBT protocols, and emergency safety guardrails.")

# Render Conversation
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👩‍⚕️" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# Chat Input
user_input = st.chat_input("What is on your heart or mind today?")
if user_input:
    # Append user turn
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Call Backend
    with st.chat_message("assistant", avatar="👩‍⚕️"):
        with st.spinner("Dr. Emily is listening..."):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={
                        "message": user_input,
                        "session_id": st.session_state.session_id
                    },
                    timeout=30
                )
                if res.status_code == 200:
                    data = res.json()
                    response_text = data["response"]

                    if data.get("is_crisis"):
                        st.error("⚠️ Emergency crisis protocol activated.")

                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    err_msg = "I'm having technical difficulties connecting, but I want you to know your feelings matter. Please try again shortly."
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
            except Exception as e:
                err_msg = f"Connection error: Please ensure FastAPI backend is running on port 8000."
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})