#!/usr/bin/env python3
"""Script to create the complete ADK A2A Gemini project structure."""

import os
from pathlib import Path

def create_project_structure():
    """Create the complete project directory structure."""
    
    print("🚀 Creating ADK A2A Gemini Project Structure")
    print("=" * 60)
    
    # Project structure definition
    structure = {
        # Root files
        "pyproject.toml": "file",
        "requirements.txt": "file", 
        "setup.py": "file",
        ".env.example": "file",
        ".gitignore": "file",
        "README.md": "file",
        "LICENSE": "file",
        "config.py": "file",
        "__init__.py": "file",
        
        # Core directory
        "core": "directory",
        "core/__init__.py": "file",
        "core/mcp_tools.py": "file",
        "core/base_agent.py": "file",
        
        # Agents directory
        "agents": "directory",
        "agents/__init__.py": "file",
        
        # Notion Agent
        "agents/notion_agent": "directory",
        "agents/notion_agent/__init__.py": "file",
        "agents/notion_agent/agent.py": "file",
        "agents/notion_agent/prompt.py": "file",
        "agents/notion_agent/__main__.py": "file",
        "agents/notion_agent/executor.py": "file",
        
        # ElevenLabs Agent
        "agents/elevenlabs_agent": "directory",
        "agents/elevenlabs_agent/__init__.py": "file",
        "agents/elevenlabs_agent/agent.py": "file",
        "agents/elevenlabs_agent/prompt.py": "file",
        "agents/elevenlabs_agent/__main__.py": "file",
        "agents/elevenlabs_agent/executor.py": "file",
        
        # Host Agent
        "agents/host_agent": "directory",
        "agents/host_agent/__init__.py": "file",
        "agents/host_agent/agent.py": "file",
        "agents/host_agent/prompt.py": "file",
        "agents/host_agent/__main__.py": "file",
        "agents/host_agent/executor.py": "file",
        "agents/host_agent/tools.py": "file",
        
        # UI directory
        "ui": "directory",
        "ui/__init__.py": "file",
        "ui/streamlit_app.py": "file",
        "ui/components": "directory",
        "ui/components/__init__.py": "file",
        "ui/components/chat.py": "file",
        
        # Scripts directory
        "scripts": "directory",
        "scripts/__init__.py": "file",
        "scripts/install_deps.py": "file",
        "scripts/test_setup.py": "file",
        "scripts/start_agents.py": "file",
        "scripts/setup_project.py": "file",
        
        # Tests directory
        "tests": "directory",
        "tests/__init__.py": "file",
        "tests/test_agents.py": "file",
        "tests/test_mcp.py": "file",
        "tests/test_integration.py": "file",
        
        # Logs directory (will be created at runtime)
        "logs": "directory",
        "logs/.gitkeep": "file",
    }
    
    created_dirs = 0
    created_files = 0
    
    print("\n📁 Creating directories and files...")
    
    # Create structure
    for path, item_type in structure.items():
        try:
            if item_type == "directory":
                Path(path).mkdir(parents=True, exist_ok=True)
                print(f"📁 Created directory: {path}")
                created_dirs += 1
            elif item_type == "file":
                # Create parent directories if they don't exist
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                
                # Create empty file if it doesn't exist
                if not Path(path).exists():
                    Path(path).touch()
                    print(f"📄 Created file: {path}")
                    created_files += 1
                else:
                    print(f"⏭️  File already exists: {path}")
        except Exception as e:
            print(f"❌ Error creating {path}: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   📁 Directories created: {created_dirs}")
    print(f"   📄 Files created: {created_files}")
    
    # Create file content templates
    create_file_templates()
    
    print("\n🎉 Project structure created successfully!")
    print("\n📋 Next Steps:")
    print("1. Copy the content from artifacts into the corresponding files")
    print("2. Here's the mapping of files to copy:")
    
    file_mapping = {
        "pyproject.toml": "pyproject_toml_new",
        "requirements.txt": "requirements_txt_new", 
        "setup.py": "setup_py_new",
        ".env.example": "env_example_new",
        "config.py": "config_py_new",
        "core/mcp_tools.py": "core_mcp_tools",
        "core/base_agent.py": "core_base_agent",
        "agents/notion_agent/agent.py": "notion_agent_complete",
        "agents/notion_agent/prompt.py": "notion_agent_prompt",
        "agents/notion_agent/__main__.py": "notion_agent_main",
        "agents/notion_agent/executor.py": "notion_agent_executor",
        "agents/elevenlabs_agent/agent.py": "elevenlabs_agent_complete",
        "agents/elevenlabs_agent/prompt.py": "elevenlabs_agent_prompt",
        "agents/host_agent/agent.py": "host_agent_complete",
        "agents/host_agent/prompt.py": "host_agent_prompt",
        "agents/host_agent/tools.py": "host_agent_tools",
        "ui/streamlit_app.py": "ui_streamlit_app",
        "scripts/install_deps.py": "scripts_install_deps",
        "scripts/test_setup.py": "scripts_test_setup",
        "scripts/start_agents.py": "scripts_start_agents",
        "README.md": "project_readme"
    }
    
    print("\n📋 File Copy Guide:")
    for file_path, artifact_name in file_mapping.items():
        print(f"   📄 {file_path} ← Copy from artifact '{artifact_name}'")
    
    print(f"\n📄 Additional files to copy from 'complete_setup_script' artifact:")
    print(f"   📄 agents/elevenlabs_agent/__main__.py")
    print(f"   📄 agents/elevenlabs_agent/executor.py")
    print(f"   📄 agents/host_agent/__main__.py")
    print(f"   📄 agents/host_agent/executor.py")

def create_file_templates():
    """Create basic templates for some files."""
    print("\n📝 Creating basic file templates...")
    
    # .gitignore
    gitignore_content = """# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Logs
*.log
logs/

# Jupyter Notebook
.ipynb_checkpoints

# Local development
.DS_Store

# Distribution
*.bak
*.tmp
*.temp
"""
    
    # LICENSE
    license_content = """MIT License

Copyright (c) [2025] [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    # UI chat component
    chat_component = '''"""Chat component for Streamlit UI."""

import streamlit as st
from typing import List, Dict, Any

def display_chat_message(message: Dict[str, Any]):
    """Display a single chat message."""
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        if message.get("tool_calls"):
            with st.expander(f"🛠️ Tool Calls ({len(message['tool_calls'])})", expanded=False):
                for call in message["tool_calls"]:
                    st.code(f"Tool: {call['name']}\\nArguments: {call['args']}", language="json")
        
        if message.get("tool_responses"):
            with st.expander(f"⚡ Tool Responses ({len(message['tool_responses'])})", expanded=False):
                for response in message["tool_responses"]:
                    st.write(f"**{response['name']}:**")
                    st.text(str(response['response']))

def display_conversation_history(conversation: List[Dict[str, Any]]):
    """Display the full conversation history."""
    for message in conversation:
        display_chat_message(message)
'''
    
    # Basic test files
    test_agents = '''"""Test agents functionality."""

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
'''
    
    test_mcp = '''"""Test MCP tools functionality."""

import pytest

def test_mcp_imports():
    """Test that MCP tools can be imported."""
    try:
        from core.mcp_tools import mcp_manager
        assert mcp_manager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import MCP tools: {e}")
'''
    
    test_integration = '''"""Integration tests."""

import pytest

def test_config_validation():
    """Test configuration validation."""
    try:
        import config
        # Test config loading
        summary = config.get_config_summary()
        assert isinstance(summary, dict)
    except Exception as e:
        pytest.fail(f"Config test failed: {e}")
'''
    
    setup_project = '''"""Setup project script."""

import sys
from pathlib import Path

def main():
    """Setup the project."""
    print("🚀 Setting up ADK A2A Gemini project...")
    
    # Add any additional setup logic here
    print("✅ Project setup complete!")
    print("Run: python scripts/install_deps.py")

if __name__ == "__main__":
    main()
'''
    
    # Write template files
    templates = {
        ".gitignore": gitignore_content,
        "LICENSE": license_content,
        "ui/components/chat.py": chat_component,
        "tests/test_agents.py": test_agents,
        "tests/test_mcp.py": test_mcp,
        "tests/test_integration.py": test_integration,
        "scripts/setup_project.py": setup_project,
        "logs/.gitkeep": "# This file keeps the logs directory in version control\n"
    }
    
    for file_path, content in templates.items():
        try:
            Path(file_path).write_text(content, encoding='utf-8')
            print(f"📝 Created template: {file_path}")
        except Exception as e:
            print(f"❌ Error creating template {file_path}: {e}")

if __name__ == "__main__":
    create_project_structure()