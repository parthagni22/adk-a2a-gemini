"""Base agent class with common functionality."""

import logging
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

import config

logger = logging.getLogger(__name__)

class BaseADKAgent(ABC):
    """Base class for all ADK agents."""
    
    def __init__(self, name: str, description: str, model_name: str = "gemini/gemini-2.0-flash"):
        self.name = name
        self.description = description
        self.model_name = model_name
        self._agent: Optional[Agent] = None
        self._agent_card: Optional[AgentCard] = None
    
    @abstractmethod
    def get_instruction(self) -> str:
        """Get the agent's instruction prompt."""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Any]:
        """Get the agent's tools."""
        pass
    
    @abstractmethod
    def get_skills(self) -> List[AgentSkill]:
        """Get the agent's skills for the agent card."""
        pass
    
    def create_agent(self) -> Agent:
        """Create the ADK agent."""
        if self._agent is None:
            try:
                self._agent = Agent(
                    name=self.name,
                    model=LiteLlm(model=self.model_name, api_key=config.GOOGLE_API_KEY),
                    description=self.description,
                    instruction=self.get_instruction(),
                    tools=self.get_tools()
                )
                logger.info(f"Created agent: {self.name}")
            except Exception as e:
                logger.error(f"Failed to create agent {self.name}: {e}")
                raise
        
        return self._agent
    
    def create_agent_card(self, host: str, port: int) -> AgentCard:
        """Create the A2A agent card."""
        if self._agent_card is None:
            self._agent_card = AgentCard(
                name=self.name,
                description=self.description,
                url=f"http://{host}:{port}/",
                version="1.0.0",
                defaultInputModes=["text"],
                defaultOutputModes=["text"],
                capabilities=AgentCapabilities(
                    streaming=False,
                    pushNotifications=False
                ),
                skills=self.get_skills()
            )
        
        return self._agent_card
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent."""
        return {
            "name": self.name,
            "description": self.description,
            "model": self.model_name,
            "skills": [skill.name for skill in self.get_skills()],
            "tools_count": len(self.get_tools()),
        }

class MockTool:
    """Mock tool for testing without real MCP connections."""
    
    def __init__(self, name: str, description: str, mock_response: str):
        self.name = name
        self.description = description
        self.mock_response = mock_response
    
    def __call__(self, *args, **kwargs) -> str:
        """Execute the mock tool."""
        return self.mock_response.format(**kwargs) if kwargs else self.mock_response

def create_notion_search_tool() -> MockTool:
    """Create a mock Notion search tool."""
    return MockTool(
        name="notion_search",
        description="Search Notion workspace for pages and content",
        mock_response="""🔍 **Notion Search Results**

Found several pages related to your query:

📄 **Project Documentation**
   - Contains comprehensive project information
   - Last updated: 2 days ago
   - URL: https://notion.so/project-docs

📄 **Meeting Notes**  
   - Recent team discussions and decisions
   - Last updated: 1 week ago
   - URL: https://notion.so/meeting-notes

📄 **Task Management**
   - Current project tasks and status
   - Last updated: Today
   - URL: https://notion.so/tasks

*Note: This is a demonstration response. Real Notion integration requires proper API setup.*"""
    )

def create_notion_database_tool() -> MockTool:
    """Create a mock Notion database tool."""
    return MockTool(
        name="notion_database",
        description="Query Notion databases for structured data",
        mock_response="""📊 **Database Query Results**

**Database**: Sermon Notes
**Total entries**: 127
**Last updated**: Today

**Recent entries:**
1. "Walking in Faith: Steps of obedience" (July 7, 2025)
2. "Knowing the heart of God: Real repentance" (June 8, 2025)  
3. "The cross of Christ: Scorned" (April 6, 2025)

**Categories**: 
- Gospel Freedom (23 entries)
- Transforming Grace (18 entries)
- Stand Firm (15 entries)

*Note: This is a demonstration response. Real database queries require proper Notion API setup.*"""
    )

def create_text_to_speech_tool() -> MockTool:
    """Create a mock text-to-speech tool."""
    return MockTool(
        name="text_to_speech",
        description="Convert text to speech using ElevenLabs",
        mock_response="""🎵 **Text-to-Speech Complete**

✅ Successfully converted text to speech
🎙️ Voice: Default ElevenLabs voice
📁 Audio file: `/tmp/audio_{timestamp}.mp3`
⏱️ Duration: ~{duration} seconds
🔊 Quality: High (22kHz, 128kbps)

*Note: This is a demonstration response. Real audio generation requires ElevenLabs API integration.*"""
    )