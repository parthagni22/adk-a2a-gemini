"""Configuration settings for ADK A2A Gemini project."""

import os
from typing import Final
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY: Final[str] = os.getenv("GOOGLE_API_KEY", "")
NOTION_API_KEY: Final[str] = os.getenv("NOTION_API_KEY", "")
ELEVENLABS_API_KEY: Final[str] = os.getenv("ELEVENLABS_API_KEY", "")

# Agent Ports
NOTION_AGENT_PORT: Final[int] = int(os.getenv("NOTION_AGENT_PORT", "8002"))
ELEVENLABS_AGENT_PORT: Final[int] = int(os.getenv("ELEVENLABS_AGENT_PORT", "8003"))
HOST_AGENT_PORT: Final[int] = int(os.getenv("HOST_AGENT_PORT", "8001"))

# Agent URLs
NOTION_AGENT_URL: Final[str] = os.getenv("NOTION_AGENT_URL", f"http://localhost:{NOTION_AGENT_PORT}")
ELEVENLABS_AGENT_URL: Final[str] = os.getenv("ELEVENLABS_AGENT_URL", f"http://localhost:{ELEVENLABS_AGENT_PORT}")
HOST_AGENT_URL: Final[str] = os.getenv("HOST_AGENT_URL", f"http://localhost:{HOST_AGENT_PORT}")

# MCP Configuration
MCP_TIMEOUT: Final[int] = int(os.getenv("MCP_TIMEOUT", "180"))
MCP_RETRY_ATTEMPTS: Final[int] = int(os.getenv("MCP_RETRY_ATTEMPTS", "3"))

# Logging
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")
LOG_TO_FILE: Final[bool] = os.getenv("LOG_TO_FILE", "true").lower() == "true"

# UI Configuration
UI_PORT: Final[int] = int(os.getenv("UI_PORT", "8080"))
UI_TITLE: Final[str] = os.getenv("UI_TITLE", "ADK A2A Assistant")

# Development
DEBUG: Final[bool] = os.getenv("DEBUG", "false").lower() == "true"
DEVELOPMENT_MODE: Final[bool] = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"

# Validation
def validate_config() -> list[str]:
    """Validate configuration and return list of missing required settings."""
    errors = []
    
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is required")
    
    if not NOTION_API_KEY:
        errors.append("NOTION_API_KEY is required")
    
    if not ELEVENLABS_API_KEY:
        errors.append("ELEVENLABS_API_KEY is required")
    
    return errors

def get_config_summary() -> dict:
    """Get a summary of current configuration (without sensitive data)."""
    return {
        "google_api_key_set": bool(GOOGLE_API_KEY),
        "notion_api_key_set": bool(NOTION_API_KEY),
        "elevenlabs_api_key_set": bool(ELEVENLABS_API_KEY),
        "notion_agent_port": NOTION_AGENT_PORT,
        "elevenlabs_agent_port": ELEVENLABS_AGENT_PORT,
        "host_agent_port": HOST_AGENT_PORT,
        "log_level": LOG_LEVEL,
        "debug": DEBUG,
    }