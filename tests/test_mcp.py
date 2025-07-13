"""Test MCP tools functionality."""

import pytest

def test_mcp_imports():
    """Test that MCP tools can be imported."""
    try:
        from core.mcp_tools import mcp_manager
        assert mcp_manager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import MCP tools: {e}")
