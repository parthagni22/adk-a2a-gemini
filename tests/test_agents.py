"""Test agents functionality."""

import pytest
import asyncio

def test_import_agents():
    """Test that all agents can be imported."""
    try:
        from agents.notion_agent.agent import create_notion_agent
        from agents.elevenlabs_agent.agent import create_elevenlabs_agent
        from agents.host_agent.agent import create_host_agent
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import agents: {e}")

@pytest.mark.asyncio
async def test_agent_creation():
    """Test agent creation."""
    # This test would need proper config setup
    pass
