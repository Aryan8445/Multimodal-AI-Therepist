import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="Multimodal AI Therapist", page_icon=":robot_face:")
st.title("Multimodal AI Therapist")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("What would you like to talk about?")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    response = requests.post(BACKEND_URL, json={"message": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": f'{response.json()["response"]} WITH TOOL: [{response.json()["tool_used"]}]'})

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])