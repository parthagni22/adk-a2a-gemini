"""Streamlit UI for the ADK A2A Gemini project."""

import asyncio
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
import httpx

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import config
from agents.host_agent.agent import create_host_agent
from google.adk.runners import Runner
from google.genai import types

# Page configuration
st.set_page_config(
    page_title=config.UI_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class HostAgentRunner:
    """Manages the Host Agent for the UI."""
    
    def __init__(self):
        self.runner = None
        self.agent = None
        self.app_name = "streamlit_host_agent"
        self.user_id = "streamlit_user"
    
    @st.cache_resource
    def get_runner(_self):
        """Get or create the ADK runner (cached)."""
        try:
            _self.agent = create_host_agent()
            _self.runner = Runner(
                agent=_self.agent,
                app_name=_self.app_name
            )
            return _self.runner
        except Exception as e:
            st.error(f"Failed to create Host Agent: {e}")
            return None
    
    async def run_agent(self, prompt: str, session_id: str) -> Dict[str, Any]:
        """Run the host agent with a prompt."""
        try:
            if not self.runner:
                self.runner = self.get_runner()
            
            if not self.runner:
                return {"error": "Failed to initialize agent"}
            
            # Ensure session exists
            if 'adk_session_initialized' not in st.session_state:
                try:
                    await self.runner.session_service.create_session(
                        app_name=self.app_name,
                        user_id=self.user_id,
                        session_id=session_id
                    )
                    st.session_state.adk_session_initialized = True
                except Exception:
                    st.session_state.adk_session_initialized = True
            
            # Track conversation
            tool_calls = []
            tool_responses = []
            final_response = ""
            
            # Run the agent
            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=session_id,
                new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # Handle function calls
                        if part.function_call:
                            tool_calls.append({
                                'name': part.function_call.name,
                                'args': part.function_call.args
                            })
                        
                        # Handle function responses
                        elif part.function_response:
                            tool_responses.append({
                                'name': part.function_response.name,
                                'response': part.function_response.response
                            })
                
                # Handle final response
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response = "".join([p.text for p in event.content.parts if p.text])
                    break
            
            return {
                'success': True,
                'final_response': final_response,
                'tool_calls': tool_calls,
                'tool_responses': tool_responses
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'final_response': f"Error: {str(e)}",
                'tool_calls': [],
                'tool_responses': []
            }

def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session-{uuid.uuid4()}"
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'agent_runner' not in st.session_state:
        st.session_state.agent_runner = HostAgentRunner()

def check_agent_status() -> Dict[str, bool]:
    """Check if agents are running."""
    agents = {
        "notion": config.NOTION_AGENT_URL,
        "elevenlabs": config.ELEVENLABS_AGENT_URL,
        "host": config.HOST_AGENT_URL
    }
    
    status = {}
    for agent_name, url in agents.items():
        try:
            # Use requests with a short timeout
            import requests
            response = requests.get(f"{url}/.well-known/agent.json", timeout=2)
            status[agent_name] = response.status_code == 200
        except:
            status[agent_name] = False
    
    return status

def display_tool_calls(tool_calls: List[Dict[str, Any]]):
    """Display tool calls in an expandable section."""
    if tool_calls:
        with st.expander(f"🛠️ Tool Calls ({len(tool_calls)})", expanded=False):
            for i, call in enumerate(tool_calls, 1):
                st.markdown(f"**Call {i}: {call['name']}**")
                if call.get('args'):
                    st.code(str(call['args']), language="json")

def display_tool_responses(tool_responses: List[Dict[str, Any]]):
    """Display tool responses in an expandable section."""
    if tool_responses:
        with st.expander(f"⚡ Tool Responses ({len(tool_responses)})", expanded=False):
            for i, response in enumerate(tool_responses, 1):
                st.markdown(f"**Response {i}: {response['name']}**")
                if isinstance(response['response'], str):
                    st.markdown(response['response'])
                else:
                    st.json(response['response'])

def main():
    """Main Streamlit application."""
    # Initialize session state
    initialize_session_state()
    
    # Main title
    st.title("🤖 ADK A2A Assistant")
    st.markdown("*Powered by Google Gemini, Notion, and ElevenLabs*")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Configuration check
        config_errors = config.validate_config()
        if config_errors:
            st.error("Configuration Issues:")
            for error in config_errors:
                st.write(f"❌ {error}")
            st.info("Please check your .env file")
        else:
            st.success("✅ Configuration OK")
        
        # Agent status
        with st.spinner("Checking agent status..."):
            agent_status = check_agent_status()
        
        st.subheader("Agent Status")
        for agent_name, is_running in agent_status.items():
            status_icon = "✅" if is_running else "❌"
            status_text = "Running" if is_running else "Stopped"
            st.write(f"{status_icon} {agent_name.title()}: {status_text}")
        
        if not all(agent_status.values()):
            st.warning("⚠️ Some agents are not running")
            st.info("Run: `python scripts/start_agents.py`")
        
        # Session info
        st.subheader("Session Info")
        st.write(f"Session ID: `{st.session_state.session_id[:8]}...`")
        
        if st.button("🔄 New Session"):
            # Clear conversation but keep agent runner
            st.session_state.conversation_history = []
            st.session_state.session_id = f"session-{uuid.uuid4()}"
            st.rerun()
        
        # Example queries
        st.subheader("💡 Example Queries")
        example_queries = [
            "Search my Notion workspace for 'project documentation'",
            "Count how many entries are in the 'Sermon Notes' database",
            "Convert this text to speech: 'Hello from ADK A2A!'",
            "Find my meeting notes and read the summary aloud"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.example_query = query
                st.rerun()
    
    # Main chat interface
    st.subheader("💬 Chat with Your Assistant")
    
    # Display conversation history
    for message in st.session_state.conversation_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Show tool interactions if present
            if message.get("tool_calls"):
                display_tool_calls(message["tool_calls"])
            if message.get("tool_responses"):
                display_tool_responses(message["tool_responses"])
    
    # Handle example query
    prompt = None
    if hasattr(st.session_state, 'example_query'):
        prompt = st.session_state.example_query
        delattr(st.session_state, 'example_query')
    
    # Chat input
    if not prompt:
        prompt = st.chat_input("Ask me to search Notion, create audio, or coordinate tasks...")
    
    if prompt:
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process with agent
        with st.chat_message("assistant"):
            with st.spinner("🤔 Processing your request..."):
                # Run agent logic
                result = asyncio.run(
                    st.session_state.agent_runner.run_agent(prompt, st.session_state.session_id)
                )
            
            # Display results
            if result.get('success'):
                if result['final_response']:
                    st.write(result['final_response'])
                
                # Show tool interactions
                display_tool_calls(result['tool_calls'])
                display_tool_responses(result['tool_responses'])
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": result['final_response'],
                    "tool_calls": result['tool_calls'],
                    "tool_responses": result['tool_responses']
                })
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                st.error(f"❌ Error: {error_msg}")
                
                # Add error to conversation history
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": f"I encountered an error: {error_msg}",
                    "tool_calls": [],
                    "tool_responses": []
                })
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>
            🚀 Built with ADK A2A | 🧠 Powered by Google Gemini | 
            📝 Notion Integration | 🎵 ElevenLabs TTS
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()