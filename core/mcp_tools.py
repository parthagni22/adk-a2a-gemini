"""Simplified MCP tools with proper error handling."""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
from datetime import timedelta

from mcp import StdioServerParameters
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

import config

logger = logging.getLogger(__name__)

class SimpleMCPTool:
    """Base class for simplified MCP tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.session: Optional[ClientSession] = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to MCP server. Override in subclasses."""
        return False
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.session:
            await self.session.close()
            self.session = None
        self.connected = False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the MCP server."""
        if not self.connected:
            return f"Error: Not connected to {self.name} MCP server"
        
        try:
            if self.session:
                result = await self.session.call_tool(tool_name, arguments)
                return str(result.content[0].text if result.content else "No response")
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return f"Error calling {tool_name}: {str(e)}"

class NotionMCPTool(SimpleMCPTool):
    """Notion MCP tool with fallback to mock responses."""
    
    def __init__(self):
        super().__init__("notion", "Notion workspace integration")
    
    async def connect(self) -> bool:
        """Connect to Notion MCP server."""
        try:
            # Try to connect to real Notion MCP server
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@notionhq/notion-mcp-server"],
                env={
                    "OPENAPI_MCP_HEADERS": json.dumps({
                        "Authorization": f"Bearer {config.NOTION_API_KEY}",
                        "Notion-Version": "2022-06-28"
                    })
                }
            )
            
            client = stdio_client(server=server_params)
            read, write = await client.__aenter__()
            
            self.session = ClientSession(read, write)
            await self.session.initialize()
            
            self.connected = True
            logger.info("Connected to Notion MCP server")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to connect to Notion MCP server: {e}")
            logger.info("Using mock Notion responses")
            self.connected = True  # Use mock mode
            return True
    
    async def search_pages(self, query: str) -> str:
        """Search Notion pages."""
        if not self.connected:
            return "Error: Not connected to Notion"
        
        try:
            if self.session:
                # Real MCP call
                result = await self.call_tool("notion.search", {"query": query})
                return result
            else:
                # Mock response
                return f"""Found Notion pages for '{query}':
                
📄 **Project Documentation** 
   - Contains information about {query}
   - Last updated: 2 days ago
   - URL: https://notion.so/project-docs
   
📄 **Meeting Notes - {query}**
   - Discussion about {query} implementation
   - Last updated: 1 week ago  
   - URL: https://notion.so/meeting-notes
   
🔍 *Note: This is a mock response. Real Notion integration requires proper MCP setup.*"""
                
        except Exception as e:
            return f"Error searching Notion: {str(e)}"
    
    async def query_database(self, database_name: str) -> str:
        """Query a Notion database."""
        try:
            if self.session:
                # Real MCP call would go here
                result = await self.call_tool("notion.queryDatabase", {"database": database_name})
                return result
            else:
                # Mock response
                return f"""Database '{database_name}' contains:

📊 **Total entries**: 42
📅 **Last updated**: Today
🏷️ **Categories**: Projects, Notes, Tasks

**Recent entries:**
1. Entry about project planning
2. Meeting notes from yesterday  
3. Task list for this week

🔍 *Note: This is a mock response. Real Notion database queries require proper MCP setup.*"""
                
        except Exception as e:
            return f"Error querying database '{database_name}': {str(e)}"

class ElevenLabsMCPTool(SimpleMCPTool):
    """ElevenLabs MCP tool with fallback to mock responses."""
    
    def __init__(self):
        super().__init__("elevenlabs", "Text-to-speech conversion")
    
    async def connect(self) -> bool:
        """Connect to ElevenLabs MCP server (mock for now)."""
        try:
            # Since elevenlabs-mcp doesn't exist, we'll use mock mode
            logger.info("Using mock ElevenLabs responses (real MCP server not available)")
            self.connected = True
            return True
            
        except Exception as e:
            logger.warning(f"Failed to connect to ElevenLabs MCP server: {e}")
            self.connected = True  # Use mock mode anyway
            return True
    
    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech."""
        if not self.connected:
            return "Error: Not connected to ElevenLabs"
        
        try:
            # Mock response since real ElevenLabs MCP doesn't exist
            import time
            timestamp = int(time.time())
            audio_path = f"/tmp/audio_{timestamp}.mp3"
            
            return f"""✅ Text-to-speech conversion completed!

📝 **Text**: "{text[:100]}{'...' if len(text) > 100 else ''}"
🎵 **Audio file**: `{audio_path}`
🎙️ **Voice**: Default ElevenLabs voice
⏱️ **Duration**: ~{len(text.split()) * 0.5:.1f} seconds

🔍 *Note: This is a mock response. Real audio generation requires ElevenLabs API integration.*"""
            
        except Exception as e:
            return f"Error converting text to speech: {str(e)}"

class MCPToolManager:
    """Manager for all MCP tools."""
    
    def __init__(self):
        self.notion_tool = NotionMCPTool()
        self.elevenlabs_tool = ElevenLabsMCPTool()
        self.tools = {
            "notion": self.notion_tool,
            "elevenlabs": self.elevenlabs_tool
        }
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all MCP tools."""
        results = {}
        for name, tool in self.tools.items():
            try:
                success = await tool.connect()
                results[name] = success
                logger.info(f"MCP tool '{name}': {'Connected' if success else 'Failed'}")
            except Exception as e:
                logger.error(f"Error connecting to {name}: {e}")
                results[name] = False
        
        return results
    
    async def disconnect_all(self):
        """Disconnect from all MCP tools."""
        for tool in self.tools.values():
            try:
                await tool.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting tool: {e}")
    
    def get_tool(self, name: str) -> Optional[SimpleMCPTool]:
        """Get a specific MCP tool."""
        return self.tools.get(name)

# Global MCP manager instance
mcp_manager = MCPToolManager()