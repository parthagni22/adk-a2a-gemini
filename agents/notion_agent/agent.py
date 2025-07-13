"""Notion Agent implementation with MCP integration."""

import logging
from typing import Any, List

from google.adk.agents import Agent
from a2a.types import AgentSkill

from core.base_agent import BaseADKAgent, create_notion_search_tool, create_notion_database_tool
from core.mcp_tools import mcp_manager
from agents.notion_agent.prompt import NOTION_PROMPT

logger = logging.getLogger(__name__)

class NotionAgent(BaseADKAgent):
    """Notion agent for workspace information retrieval."""
    
    def __init__(self):
        super().__init__(
            name="notion_agent",
            description="Specialized agent for retrieving information from Notion workspace",
            model_name="gemini-2.0-flash"
        )
    
    def get_instruction(self) -> str:
        """Get the agent's instruction prompt."""
        return NOTION_PROMPT
    
    def get_tools(self) -> List[Any]:
        """Get the agent's tools."""
        # For now, return mock tools. Real MCP tools can be added later.
        return [
            create_notion_search_tool(),
            create_notion_database_tool(),
        ]
    
    def get_skills(self) -> List[AgentSkill]:
        """Get the agent's skills for the agent card."""
        return [
            AgentSkill(
                id="notion_search",
                name="Search Notion Workspace",
                description="Search for pages, blocks, and content in Notion workspace",
                tags=["notion", "search", "workspace", "pages"],
                examples=[
                    "Search for 'project documentation'",
                    "Find pages about 'meeting notes'",
                    "Look for content related to 'Q3 planning'",
                    "Find pages about sermon_notes_dummy"
                ]
            ),
            AgentSkill(
                id="notion_database",
                name="Query Notion Databases",
                description="Query and analyze Notion databases for structured information",
                tags=["notion", "database", "query", "data"],
                examples=[
                    "Count entries in 'Sermon Notes' database",
                    "Get recent entries from project database",
                    "Analyze task completion rates"
                ]
            )
        ]
    
    async def search_workspace(self, query: str) -> str:
        """Search the Notion workspace."""
        try:
            notion_tool = mcp_manager.get_tool("notion")
            if notion_tool and notion_tool.connected:
                return await notion_tool.search_pages(query)
            else:
                # Fallback to mock response
                mock_tool = create_notion_search_tool()
                return mock_tool(query=query)
        except Exception as e:
            logger.error(f"Error searching Notion workspace: {e}")
            return f"Error searching workspace: {str(e)}"
    
    async def query_database(self, database_name: str) -> str:
        """Query a Notion database."""
        try:
            notion_tool = mcp_manager.get_tool("notion")
            if notion_tool and notion_tool.connected:
                return await notion_tool.query_database(database_name)
            else:
                # Fallback to mock response
                mock_tool = create_notion_database_tool()
                return mock_tool(database=database_name)
        except Exception as e:
            logger.error(f"Error querying Notion database: {e}")
            return f"Error querying database: {str(e)}"

def create_notion_agent() -> Agent:
    """Create and return a Notion agent."""
    agent_impl = NotionAgent()
    return agent_impl.create_agent()

# For backward compatibility
root_agent = create_notion_agent()