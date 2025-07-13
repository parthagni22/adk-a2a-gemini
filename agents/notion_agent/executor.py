"""Notion Agent Executor for A2A integration."""

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

class NotionADKAgentExecutor(AgentExecutor):
    """ADK Agent Executor for Notion A2A integration."""

    def __init__(self, agent: Agent, agent_card: AgentCard, runner: Runner):
        """Initialize the Notion agent executor.

        Args:
            agent: The Notion ADK agent instance
            agent_card: Agent card for A2A service registration
            runner: Pre-configured ADK Runner instance
        """
        logger.info(f"Initializing NotionADKAgentExecutor for agent: {agent.name}")
        self.agent = agent
        self.agent_card = agent_card
        self.runner = runner
        self.session_service = runner.session_service
        self.artifact_service = runner.artifact_service

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Execute the Notion agent's logic for a given request context.

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
            logger.warning("No user input found; using default search")
            user_input = "Search for recent pages"

        logger.info(f"Processing Notion search query: '{user_input}'")
        return user_input

    def _get_session_identifiers(self, context: RequestContext) -> tuple[str, str]:
        """Get user_id and session_id for ADK session management."""
        user_id = "a2a_notion_user"
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

        logger.debug(f"Running Notion agent with session {session_id}")
        events_async: AsyncGenerator[Event, None] = self.runner.run_async(
            user_id=user_id, session_id=session_id, new_message=request_content
        )

        final_message_text = "(No search results found)"

        async for event in events_async:
            if (
                event.is_final_response()
                and event.content
                and event.content.role == "model"
            ):
                if event.content.parts and event.content.parts[0].text:
                    final_message_text = event.content.parts[0].text
                    logger.info(f"Notion agent response: {final_message_text[:200]}...")
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
        logger.info(f"Sending Notion search response for task {context.task_id}")
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
        logger.error(f"Error executing Notion search: {str(error)}", exc_info=True)
        error_message_text = f"Error searching Notion workspace: {str(error)}"
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
        logger.info(f"Cancelling Notion search task: {task_id}")

        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        canceled_status = TaskStatus(state=TaskState.canceled, timestamp=timestamp)
        cancel_event = TaskStatusUpdateEvent(
            taskId=task_id, contextId=context_id, status=canceled_status, final=True
        )
        event_queue.enqueue_event(cancel_event)
        logger.info(f"Sent cancel event for Notion task: {task_id}")