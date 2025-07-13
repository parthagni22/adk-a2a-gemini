"""Host Agent tools for A2A communication with child agents."""

import asyncio
import logging
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
import httpx

import config

logger = logging.getLogger(__name__)

# Mapping of agent names to their URLs
AGENT_URL_MAP: Dict[str, str] = {
    "notion_agent": config.NOTION_AGENT_URL,
    "elevenlabs_agent": config.ELEVENLABS_AGENT_URL,
}

class SimpleA2AClient:
    """Simplified A2A client for communication with child agents."""
    
    @staticmethod
    async def call_agent(agent_url: str, message: str) -> Dict[str, Any]:
        """Call an agent via simplified HTTP communication."""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Simplified call - in a real implementation, this would use proper A2A protocol
                response = await client.post(
                    f"{agent_url}/simple_call",
                    json={"message": message},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {"success": True, "result": result.get("response", "No response")}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
                    
        except httpx.ConnectError:
            # Agent not available, return mock response
            return await SimpleA2AClient._get_mock_response(agent_url, message)
        except Exception as e:
            logger.error(f"Error calling agent at {agent_url}: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _get_mock_response(agent_url: str, message: str) -> Dict[str, Any]:
        """Generate mock responses when agents are not available."""
        if "notion" in agent_url.lower():
            return {
                "success": True,
                "result": f"""🔍 **Notion Search Results** (Mock Response)

I would search your Notion workspace for: "{message}"

**Found pages:**
📄 Project Documentation - Contains relevant information
📄 Meeting Notes - Recent discussions about the topic  
📄 Task Database - 25 related entries found

*Note: This is a mock response. To get real results, ensure the Notion agent is running.*"""
            }
        elif "elevenlabs" in agent_url.lower():
            import time
            timestamp = int(time.time())
            return {
                "success": True,
                "result": f"""🎵 **Text-to-Speech Complete** (Mock Response)

✅ Converted to speech: "{message[:100]}{'...' if len(message) > 100 else ''}"
📁 Audio file: `/tmp/audio_{timestamp}.mp3`
🎙️ Voice: Default ElevenLabs voice
⏱️ Duration: ~{len(message.split()) * 0.5:.1f} seconds

*Note: This is a mock response. To generate real audio, ensure the ElevenLabs agent is running.*"""
            }
        else:
            return {
                "success": True,
                "result": f"Mock response for message: {message}"
            }

async def delegate_task(agent_name: str, task_description: str) -> str:
    """
    Delegate a task to a specified child agent via A2A protocol.
    
    Args:
        agent_name: The logical name of the target agent ('notion_agent' or 'elevenlabs_agent')
        task_description: A detailed description of the task for the child agent
        
    Returns:
        The result from the child agent, or an error message
    """
    if agent_name not in AGENT_URL_MAP:
        available_agents = list(AGENT_URL_MAP.keys())
        return f"❌ Error: Agent '{agent_name}' is not available. Available agents: {available_agents}"
    
    agent_url = AGENT_URL_MAP[agent_name]
    
    try:
        logger.info(f"Delegating task to {agent_name}: {task_description[:100]}...")
        
        # Call the agent
        result = await SimpleA2AClient.call_agent(agent_url, task_description)
        
        if result["success"]:
            logger.info(f"Task delegation to {agent_name} successful")
            return result["result"]
        else:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"Task delegation to {agent_name} failed: {error_msg}")
            return f"❌ Error from {agent_name}: {error_msg}"
            
    except Exception as e:
        logger.error(f"Exception during task delegation to {agent_name}: {e}")
        return f"❌ Error delegating task to {agent_name}: {str(e)}"

def delegate_task_sync(agent_name: str, task_description: str) -> str:
    """
    Synchronous wrapper for delegate_task to be used as an ADK tool.
    
    This function handles running the async delegate_task function from a synchronous
    context, which is required for ADK tools. It intelligently handles cases where
    an asyncio event loop is already running.
    
    Args:
        agent_name: The logical name of the target agent
        task_description: A detailed description of the task
        
    Returns:
        The result from the child agent, or an error message
    """
    try:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, so we need to run in a thread
            with ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, 
                    delegate_task(agent_name, task_description)
                )
                return future.result(timeout=90)  # 90 second timeout
                
        except RuntimeError:
            # No running event loop, safe to use asyncio.run()
            return asyncio.run(delegate_task(agent_name, task_description))
            
    except Exception as e:
        logger.error(f"Error in sync delegation wrapper: {e}")
        return f"❌ Error in task delegation: {str(e)}"

# Tool metadata for ADK
delegate_task_sync.__name__ = "delegate_task_sync"
delegate_task_sync.__doc__ = """
Delegate a task to a specialized child agent.

Args:
    agent_name (str): The name of the agent ('notion_agent' or 'elevenlabs_agent')
    task_description (str): Detailed description of the task to perform

Returns:
    str: The result from the child agent
"""