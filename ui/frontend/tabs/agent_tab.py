import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))

import streamlit as st
import uuid

from ai_agent.agent import real_estate_agent

def render():
    st.header("Real Estate Agent.")

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    message_container = st.container()

    user_input = st.chat_input("I want to buy a house in Tokyo...")

    if user_input:
        st.session_state.messages.append({"role":"user","content":user_input})
        response = real_estate_agent(message= str(user_input),thread_id=st.session_state.thread_id)
        st.session_state.messages.append({"role":"assistant","content":response})

    # display chat messages from history on app rerun.
    with message_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])