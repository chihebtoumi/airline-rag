import streamlit as st
from chains.chatbot import KnowledgeBase, update_state, external_chain

st.set_page_config(page_title="SkyFlow Assistant", page_icon="✈️")
st.title("✈️ SkyFlow Airline Assistant")

# Per-session memory (survives Streamlit reruns)
if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "assistant", "content": "Hello! I'm your SkyFlow agent! How can I help you?"}
    ]
if "state" not in st.session_state:
    st.session_state.state = {"know_base": KnowledgeBase()}

# Redraw the whole conversation on every rerun
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle a new message
if message := st.chat_input("Type your message..."):
    st.session_state.history.append({"role": "user", "content": message})
    with st.chat_message("user"):
        st.markdown(message)

    with st.chat_message("assistant"):
        st.session_state.state = update_state(
            st.session_state.state, message, st.session_state.history
        )
        reply = st.write_stream(external_chain.stream(st.session_state.state))

    st.session_state.history.append({"role": "assistant", "content": reply})