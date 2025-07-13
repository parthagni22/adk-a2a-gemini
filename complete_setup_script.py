#!/usr/bin/env python3
"""Script to create missing agent files."""

import os
from pathlib import Path

# ElevenLabs Agent __main__.py
elevenlabs_main = '''"""ElevenLabs Agent A2A Service Entry Point."""

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

# ADK imports
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Local imports
from agents.elevenlabs_agent.agent import ElevenLabsAgent
from agents.elevenlabs_agent.executor import ElevenLabsADKAgentExecutor
import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

@click.command()
@click.option(
    "--host",
    default="localhost",
    help="Host for the ElevenLabs agent server.",
)
@click.option(
    "--port",
    default=config.ELEVENLABS_AGENT_PORT,
    type=int,
    help="Port for the ElevenLabs agent server.",
)
def main(host: str, port: int) -> None:
    """Run the ElevenLabs ADK Agent as an A2A service."""
    
    logger.info("Starting ElevenLabs Agent A2A Service")
    
    # Check configuration
    config_errors = config.validate_config()
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    try:
        # Create agent implementation
        agent_impl = ElevenLabsAgent()
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
        agent_executor = ElevenLabsADKAgentExecutor(
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
        
        logger.info(f"🚀 Starting ElevenLabs Agent on http://{host}:{port}")
        logger.info(f"Agent: {agent_card.name} v{agent_card.version}")
        for skill in agent_card.skills:
            logger.info(f"  Skill: {skill.name} - {skill.description}")
        
        # Run the server
        uvicorn.run(a2a_app.build(), host=host, port=port, log_level="info")
        
    except Exception as e:
        logger.error(f"Failed to start ElevenLabs Agent: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

# ElevenLabs Agent executor.py
elevenlabs_executor = '''"""ElevenLabs Agent Executor for A2A integration."""

import datetime
import logging
import uuid
from collections.abc import AsyncGenerator

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    AgentCard,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import Session as ADKSession
from google.genai import types as adk_types

logger = logging.getLogger(__name__)

class ElevenLabsADKAgentExecutor(AgentExecutor):
    """ADK Agent Executor for ElevenLabs A2A integration."""

    def __init__(self, agent: Agent, agent_card: AgentCard, runner: Runner):
        """Initialize the ElevenLabs agent executor.

        Args:
            agent: The ElevenLabs ADK agent instance
            agent_card: Agent card for A2A service registration
            runner: Pre-configured ADK Runner instance
        """
        logger.info(f"Initializing ElevenLabsADKAgentExecutor for agent: {agent.name}")
        self.agent = agent
        self.agent_card = agent_card
        self.runner = runner
        self.session_service = runner.session_service
        self.artifact_service = runner.artifact_service

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute the ElevenLabs agent's logic for a given request context.

        Args:
            context: The A2A request context containing user input
            event_queue: Queue for sending events back to the A2A client
        """
        try:
            # Prepare input
            user_input = self._prepare_input(context)
            
            # Get session identifiers
            user_id, session_id = self._get_session_identifiers(context)
            
            # Ensure ADK session exists
            await self._ensure_adk_session(user_id, session_id)
            
            # Run agent and get response
            final_message_text = await self._run_agent_and_get_response(
                user_input, user_id, session_id
            )
            
            # Send response
            self._send_response(event_queue, context, final_message_text)

        except Exception as e:
            self._handle_error(e, event_queue, context)

    def _prepare_input(self, context: RequestContext) -> str:
        """Prepare and validate user input."""
        user_input = context.get_user_input()
        if not user_input:
            logger.warning("No user input found; using default text")
            user_input = "Convert 'Hello world' to speech"

        logger.info(f"Processing text-to-speech request: '{user_input}'")
        return user_input

    def _get_session_identifiers(self, context: RequestContext) -> tuple[str, str]:
        """Get user_id and session_id for ADK session management."""
        user_id = "a2a_elevenlabs_user"
        session_id = context.task_id or str(uuid.uuid4())
        return user_id, session_id

    async def _ensure_adk_session(self, user_id: str, session_id: str) -> None:
        """Create or retrieve ADK session."""
        adk_session: ADKSession | None = await self.session_service.get_session(
            app_name=self.runner.app_name, user_id=user_id, session_id=session_id
        )
        if not adk_session:
            await self.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=session_id,
                state={},
            )
            logger.info(f"Created new ADK session: {session_id}")

    async def _run_agent_and_get_response(
        self, user_input: str, user_id: str, session_id: str
    ) -> str:
        """Run the ADK agent and extract the final response."""
        request_content = adk_types.Content(
            role="user", parts=[adk_types.Part(text=user_input)]
        )

        logger.debug(f"Running ElevenLabs agent with session {session_id}")
        events_async: AsyncGenerator[Event, None] = self.runner.run_async(
            user_id=user_id, session_id=session_id, new_message=request_content
        )

        final_message_text = "(No audio generated)"

        async for event in events_async:
            if (
                event.is_final_response()
                and event.content
                and event.content.role == "model"
            ):
                if event.content.parts and event.content.parts[0].text:
                    final_message_text = event.content.parts[0].text
                    logger.info(f"ElevenLabs agent response: {final_message_text[:200]}...")
                    break
                else:
                    logger.warning("Received final event but no text in first part")
            elif event.is_final_response():
                logger.warning("Received final event without model content")

        return final_message_text

    def _send_response(
        self, event_queue: EventQueue, context: RequestContext, message_text: str
    ) -> None:
        """Send the response back via the event queue."""
        logger.info(f"Sending text-to-speech response for task {context.task_id}")
        event_queue.enqueue_event(
            new_agent_text_message(
                text=message_text,
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    def _handle_error(
        self, error: Exception, event_queue: EventQueue, context: RequestContext
    ) -> None:
        """Handle errors and send error response."""
        logger.error(f"Error executing text-to-speech: {str(error)}", exc_info=True)
        error_message_text = f"Error converting text to speech: {str(error)}"
        event_queue.enqueue_event(
            new_agent_text_message(
                text=error_message_text,
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Request the agent to cancel an ongoing task.

        Args:
            context: The A2A request context
            event_queue: Queue for sending cancellation events
        """
        task_id = context.task_id or "unknown_task"
        context_id = context.context_id or "unknown_context"
        logger.info(f"Cancelling text-to-speech task: {task_id}")

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        canceled_status = TaskStatus(state=TaskState.canceled, timestamp=timestamp)
        cancel_event = TaskStatusUpdateEvent(
            taskId=task_id, contextId=context_id, status=canceled_status, final=True
        )
        event_queue.enqueue_event(cancel_event)
        logger.info(f"Sent cancel event for ElevenLabs task: {task_id}")
'''

# Host Agent __main__.py
host_main = '''"""Host Agent A2A Service Entry Point."""

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

# ADK imports
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Local imports
from agents.host_agent.agent import HostAgent
from agents.host_agent.executor import HostADKAgentExecutor
import config

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

@click.command()
@click.option(
    "--host",
    default="localhost",
    help="Host for the Host agent server.",
)
@click.option(
    "--port",
    default=config.HOST_AGENT_PORT,
    type=int,
    help="Port for the Host agent server.",
)
def main(host: str, port: int) -> None:
    """Run the Host ADK Agent as an A2A service."""
    
    logger.info("Starting Host Agent A2A Service")
    
    # Check configuration
    config_errors = config.validate_config()
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    try:
        # Create agent implementation
        agent_impl = HostAgent()
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
        agent_executor = HostADKAgentExecutor(
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
        
        logger.info(f"🚀 Starting Host Agent on http://{host}:{port}")
        logger.info(f"Agent: {agent_card.name} v{agent_card.version}")
        for skill in agent_card.skills:
            logger.info(f"  Skill: {skill.name} - {skill.description}")
        
        # Run the server
        uvicorn.run(a2a_app.build(), host=host, port=port, log_level="info")
        
    except Exception as e:
        logger.error(f"Failed to start Host Agent: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

# Host Agent executor.py
host_executor = '''"""Host Agent Executor for A2A integration."""

import datetime
import logging
import uuid
from collections.abc import AsyncGenerator

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    AgentCard,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_agent_text_message
from google.adk.agents import Agent
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import Session as ADKSession
from google.genai import types as adk_types

logger = logging.getLogger(__name__)

class HostADKAgentExecutor(AgentExecutor):
    """ADK Agent Executor for Host A2A integration."""

    def __init__(self, agent: Agent, agent_card: AgentCard, runner: Runner):
        """Initialize the Host agent executor.

        Args:
            agent: The Host ADK agent instance
            agent_card: Agent card for A2A service registration
            runner: Pre-configured ADK Runner instance
        """
        logger.info(f"Initializing HostADKAgentExecutor for agent: {agent.name}")
        self.agent = agent
        self.agent_card = agent_card
        self.runner = runner
        self.session_service = runner.session_service
        self.artifact_service = runner.artifact_service

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute the Host agent's logic for a given request context.

        Args:
            context: The A2A request context containing user input
            event_queue: Queue for sending events back to the A2A client
        """
        try:
            # Prepare input
            user_input = self._prepare_input(context)
            
            # Get session identifiers
            user_id, session_id = self._get_session_identifiers(context)
            
            # Ensure ADK session exists
            await self._ensure_adk_session(user_id, session_id)
            
            # Run agent and get response
            final_message_text = await self._run_agent_and_get_response(
                user_input, user_id, session_id
            )
            
            # Send response
            self._send_response(event_queue, context, final_message_text)

        except Exception as e:
            self._handle_error(e, event_queue, context)

    def _prepare_input(self, context: RequestContext) -> str:
        """Prepare and validate user input."""
        user_input = context.get_user_input()
        if not user_input:
            logger.warning("No user input found; using default query")
            user_input = "Help me coordinate agents"

        logger.info(f"Processing orchestration request: '{user_input}'")
        return user_input

    def _get_session_identifiers(self, context: RequestContext) -> tuple[str, str]:
        """Get user_id and session_id for ADK session management."""
        user_id = "a2a_host_user"
        session_id = context.task_id or str(uuid.uuid4())
        return user_id, session_id

    async def _ensure_adk_session(self, user_id: str, session_id: str) -> None:
        """Create or retrieve ADK session."""
        adk_session: ADKSession | None = await self.session_service.get_session(
            app_name=self.runner.app_name, user_id=user_id, session_id=session_id
        )
        if not adk_session:
            await self.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=session_id,
                state={},
            )
            logger.info(f"Created new ADK session: {session_id}")

    async def _run_agent_and_get_response(
        self, user_input: str, user_id: str, session_id: str
    ) -> str:
        """Run the ADK agent and extract the final response."""
        request_content = adk_types.Content(
            role="user", parts=[adk_types.Part(text=user_input)]
        )

        logger.debug(f"Running Host agent with session {session_id}")
        events_async: AsyncGenerator[Event, None] = self.runner.run_async(
            user_id=user_id, session_id=session_id, new_message=request_content
        )

        final_message_text = "(No response generated)"

        async for event in events_async:
            if (
                event.is_final_response()
                and event.content
                and event.content.role == "model"
            ):
                if event.content.parts and event.content.parts[0].text:
                    final_message_text = event.content.parts[0].text
                    logger.info(f"Host agent response: {final_message_text[:200]}...")
                    break
                else:
                    logger.warning("Received final event but no text in first part")
            elif event.is_final_response():
                logger.warning("Received final event without model content")

        return final_message_text

    def _send_response(
        self, event_queue: EventQueue, context: RequestContext, message_text: str
    ) -> None:
        """Send the response back via the event queue."""
        logger.info(f"Sending orchestration response for task {context.task_id}")
        event_queue.enqueue_event(
            new_agent_text_message(
                text=message_text,
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    def _handle_error(
        self, error: Exception, event_queue: EventQueue, context: RequestContext
    ) -> None:
        """Handle errors and send error response."""
        logger.error(f"Error executing orchestration: {str(error)}", exc_info=True)
        error_message_text = f"Error orchestrating agents: {str(error)}"
        event_queue.enqueue_event(
            new_agent_text_message(
                text=error_message_text,
                context_id=context.context_id,
                task_id=context.task_id,
            )
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Request the agent to cancel an ongoing task.

        Args:
            context: The A2A request context
            event_queue: Queue for sending cancellation events
        """
        task_id = context.task_id or "unknown_task"
        context_id = context.context_id or "unknown_context"
        logger.info(f"Cancelling orchestration task: {task_id}")

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        canceled_status = TaskStatus(state=TaskState.canceled, timestamp=timestamp)
        cancel_event = TaskStatusUpdateEvent(
            taskId=task_id, contextId=context_id, status=canceled_status, final=True
        )
        event_queue.enqueue_event(cancel_event)
        logger.info(f"Sent cancel event for Host task: {task_id}")
'''

# Create the files
files_to_create = [
    ("agents/elevenlabs_agent/__main__.py", elevenlabs_main),
    ("agents/elevenlabs_agent/executor.py", elevenlabs_executor),
    ("agents/host_agent/__main__.py", host_main),
    ("agents/host_agent/executor.py", host_executor),
]

for file_path, content in files_to_create:
    Path(file_path).write_text(content, encoding='utf-8')
    print(f"✅ Created: {file_path}")

print("\n🎉 All missing files created successfully!")
print("\nNow you can:")
print("1. Run: python scripts/start_agents.py")
print("2. In another terminal: python -m streamlit run ui/streamlit_app.py --server.port 8080")