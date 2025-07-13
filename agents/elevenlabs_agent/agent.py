"""ElevenLabs Agent implementation with MCP integration."""

import logging
from typing import Any, List

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from a2a.types import AgentSkill

from core.base_agent import BaseADKAgent, create_text_to_speech_tool
from core.mcp_tools import mcp_manager
from agents.elevenlabs_agent.prompt import ELEVENLABS_PROMPT
import config

logger = logging.getLogger(__name__)

class ElevenLabsAgent(BaseADKAgent):
    """ElevenLabs agent for text-to-speech conversion."""
    
    def __init__(self):
        super().__init__(
            name="elevenlabs_agent",
            description="Specialized agent for converting text to speech using ElevenLabs",
            model_name="gemini/gemini-2.0-flash"
        )
    
    def get_instruction(self) -> str:
        """Get the agent's instruction prompt."""
        return ELEVENLABS_PROMPT
    
    def get_tools(self) -> List[Any]:
        """Get the agent's tools."""
        # For now, return mock tools. Real MCP tools can be added later.
        return [
            create_text_to_speech_tool(),
        ]
    
    def get_skills(self) -> List[AgentSkill]:
        """Get the agent's skills for the agent card."""
        return [
            AgentSkill(
                id="text_to_speech",
                name="Convert Text to Speech",
                description="Convert any text input into high-quality speech audio using ElevenLabs",
                tags=["tts", "audio", "speech", "elevenlabs", "voice"],
                examples=[
                    "Convert 'Hello world' to speech",
                    "Read this paragraph aloud",
                    "Generate audio for presentation script"
                ]
            ),
            AgentSkill(
                id="voice_synthesis",
                name="Voice Synthesis",
                description="Generate natural-sounding speech with various voice options",
                tags=["synthesis", "voice", "natural", "generation"],
                examples=[
                    "Use a professional voice for business content",
                    "Generate speech with emotional expression",
                    "Create audio with specific voice characteristics"
                ]
            )
        ]
    
    async def convert_text_to_speech(self, text: str, voice: str = "default") -> str:
        """Convert text to speech."""
        try:
            elevenlabs_tool = mcp_manager.get_tool("elevenlabs")
            if elevenlabs_tool and elevenlabs_tool.connected:
                return await elevenlabs_tool.text_to_speech(text)
            else:
                # Fallback to mock response
                import time
                timestamp = int(time.time())
                word_count = len(text.split())
                duration = max(1, word_count * 0.5)  # Rough estimate
                
                mock_tool = create_text_to_speech_tool()
                return mock_tool.mock_response.format(
                    timestamp=timestamp,
                    duration=f"{duration:.1f}"
                )
        except Exception as e:
            logger.error(f"Error converting text to speech: {e}")
            return f"Error converting text to speech: {str(e)}"

def create_elevenlabs_agent() -> Agent:
    """Create and return an ElevenLabs agent."""
    agent_impl = ElevenLabsAgent()
    return agent_impl.create_agent()

# For backward compatibility
root_agent = create_elevenlabs_agent()