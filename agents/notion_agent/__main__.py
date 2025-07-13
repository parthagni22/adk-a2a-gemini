"""Notion Agent A2A Service Entry Point."""

import logging
import os
import sys
from pathlib import Path

import click
import uvicorn

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# A2A server imports
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# ADK imports
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Local imports
from agents.notion_agent.agent import NotionAgent
from agents.notion_agent.executor import NotionADKAgentExecutor
import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

@click.command()
@click.option(
    "--host",
    default="localhost",
    help="Host for the Notion agent server.",
)
@click.option(
    "--port",
    default=config.NOTION_AGENT_PORT,
    type=int,
    help="Port for the Notion agent server.",
)
def main(host: str, port: int) -> None:
    """Run the Notion ADK Agent as an A2A service."""
    
    logger.info("Starting Notion Agent A2A Service")
    
    # Check configuration
    config_errors = config.validate_config()
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    try:
        # Create agent implementation
        agent_impl = NotionAgent()
        adk_agent = agent_impl.create_agent()
        agent_card = agent_impl.create_agent_card(host, port)
        
        # Initialize ADK Runner
        runner = Runner(
            agent=adk_agent,
            app_name=agent_card.name,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        
        # Create agent executor
        agent_executor = NotionADKAgentExecutor(
            agent=adk_agent,
            agent_card=agent_card,
            runner=runner
        )
        
        # Setup A2A request handler
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore()
        )
        
        # Create A2A application
        a2a_app = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )
        
        logger.info(f"🚀 Starting Notion Agent on http://{host}:{port}")
        logger.info(f"Agent: {agent_card.name} v{agent_card.version}")
        for skill in agent_card.skills:
            logger.info(f"  Skill: {skill.name} - {skill.description}")
        
        # Run the server
        uvicorn.run(a2a_app.build(), host=host, port=port, log_level="info")
        
    except Exception as e:
        logger.error(f"Failed to start Notion Agent: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()