"""Host Agent implementation for orchestrating other agents."""

import logging
from typing import Any, List

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from a2a.types import AgentSkill

from core.base_agent import BaseADKAgent
from agents.host_agent.prompt import HOST_PROMPT
from agents.host_agent.tools import delegate_task_sync
import config

logger = logging.getLogger(__name__)

class HostAgent(BaseADKAgent):
    """Host agent for orchestrating multi-agent workflows."""
    
    def __init__(self):
        super().__init__(
            name="host_agent",
            description="Master orchestrator that coordinates Notion and ElevenLabs agents via A2A protocol",
            model_name="gemini/gemini-2.0-flash"
        )
    
    def get_instruction(self) -> str:
        """Get the agent's instruction prompt."""
        return HOST_PROMPT
    
    def get_tools(self) -> List[Any]:
        """Get the agent's tools."""
        return [
            delegate_task_sync,
        ]
    
    def get_skills(self) -> List[AgentSkill]:
        """Get the agent's skills for the agent card."""
        return [
            AgentSkill(
                id="orchestrate_workflows",
                name="Orchestrate Multi-Agent Workflows",
                description="Coordinate complex workflows between Notion information retrieval and ElevenLabs text-to-speech generation",
                tags=["orchestration", "workflow", "coordination", "multi-agent", "automation"],
                examples=[
                    "Search Notion for project updates and convert to speech",
                    "Find meeting notes and generate audio summary",
                    "Retrieve documentation and create audio version",
                    "Count database entries and announce the results"
                ]
            ),
            AgentSkill(
                id="task_delegation",
                name="Intelligent Task Delegation",
                description="Analyze user requests and delegate appropriate tasks to specialized agents",
                tags=["delegation", "analysis", "routing", "optimization"],
                examples=[
                    "Route search queries to Notion agent",
                    "Send text-to-speech requests to ElevenLabs agent",
                    "Chain multiple operations across agents",
                    "Handle complex multi-step workflows"
                ]
            ),
            AgentSkill(
                id="response_synthesis",
                name="Response Synthesis",
                description="Combine and synthesize responses from multiple agents into coherent results",
                tags=["synthesis", "integration", "coordination", "results"],
                examples=[
                    "Combine search results with audio generation",
                    "Provide unified responses from multiple data sources",
                    "Create comprehensive workflow summaries",
                    "Present integrated multi-agent outputs"
                ]
            )
        ]

def create_host_agent() -> Agent:
    """Create and return a Host agent."""
    agent_impl = HostAgent()
    return agent_impl.create_agent()

# For backward compatibility
root_agent = create_host_agent()