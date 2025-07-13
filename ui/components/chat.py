"""Chat component for Streamlit UI."""

import streamlit as st
from typing import List, Dict, Any

def display_chat_message(message: Dict[str, Any]):
    """Display a single chat message."""
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        if message.get("tool_calls"):
            with st.expander(f"🛠️ Tool Calls ({len(message['tool_calls'])})", expanded=False):
                for call in message["tool_calls"]:
                    st.code(f"Tool: {call['name']}\nArguments: {call['args']}", language="json")
        
        if message.get("tool_responses"):
            with st.expander(f"⚡ Tool Responses ({len(message['tool_responses'])})", expanded=False):
                for response in message["tool_responses"]:
                    st.write(f"**{response['name']}:**")
                    st.text(str(response['response']))

def display_conversation_history(conversation: List[Dict[str, Any]]):
    """Display the full conversation history."""
    for message in conversation:
        display_chat_message(message)
