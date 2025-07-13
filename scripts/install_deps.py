#!/usr/bin/env python3
"""Working install dependencies script for ADK A2A Gemini project."""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: list, description: str, check=True) -> bool:
    """Run a command and return success status."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {' '.join(command)}")
        return False

def upgrade_pip():
    """Upgrade pip to latest version."""
    print("\n🔄 Upgrading pip...")
    return run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip")

def install_core_dependencies():
    """Install core Python dependencies individually."""
    print("\n🐍 Installing Core Python Dependencies...")
    
    # Core dependencies in order
    core_deps = [
        "python-dotenv>=1.1.0",  # Install this first for config
        "click>=8.0.0",
        "httpx>=0.28.1",
        "pydantic>=2.0.0",
        "aiofiles>=23.0.0",
    ]
    
    success = True
    for dep in core_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep], f"Installing {dep}"):
            success = False
    
    return success

def install_ml_dependencies():
    """Install ML and AI dependencies."""
    print("\n🤖 Installing AI/ML Dependencies...")
    
    ml_deps = [
        "litellm>=1.72.0",
    ]
    
    success = True
    for dep in ml_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep], f"Installing {dep}"):
            success = False
    
    return success

def install_web_dependencies():
    """Install web framework dependencies."""
    print("\n🌐 Installing Web Framework Dependencies...")
    
    web_deps = [
        "fastapi>=0.115.12",
        "uvicorn[standard]>=0.34.3",
        "streamlit>=1.45.1",
    ]
    
    success = True
    for dep in web_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep], f"Installing {dep}"):
            success = False
    
    return success

def install_adk_dependencies():
    """Install ADK and A2A dependencies."""
    print("\n🔧 Installing ADK Dependencies...")
    
    adk_deps = [
        "google-adk>=1.2.1",
        "a2a-sdk>=0.2.5",
    ]
    
    success = True
    for dep in adk_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep], f"Installing {dep}"):
            success = False
    
    return success

def install_mcp_dependencies():
    """Install MCP dependencies."""
    print("\n🔗 Installing MCP Dependencies...")
    
    # Try to install MCP
    if not run_command([sys.executable, "-m", "pip", "install", "mcp>=1.0.0"], "Installing MCP", check=False):
        print("⚠️  MCP package not available, will use mock responses")
        return True  # Continue anyway
    
    return True

def install_dev_dependencies():
    """Install development dependencies."""
    print("\n🛠️  Installing Development Dependencies...")
    
    dev_deps = [
        "pytest>=8.0.0",
        "pytest-asyncio>=0.23.0",
        "black>=25.1.0",
        "isort>=5.13.0",
    ]
    
    success = True
    for dep in dev_deps:
        if not run_command([sys.executable, "-m", "pip", "install", dep], f"Installing {dep}"):
            print(f"⚠️  Failed to install {dep} (development dependency)")
            # Don't fail for dev dependencies
    
    return success

def install_node_dependencies():
    """Install Node.js dependencies if available."""
    print("\n📦 Installing Node.js Dependencies...")
    
    # Check if npm is available
    try:
        result = subprocess.run(["npm", "--version"], check=True, capture_output=True, text=True)
        print(f"✅ npm available: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  npm not found. Skipping Node.js dependencies.")
        print("   Note: Some MCP features may not work without Node.js packages.")
        print("   Install Node.js from https://nodejs.org/ to enable full MCP functionality.")
        return True
    
    # Install Node packages
    node_packages = [
        "@modelcontextprotocol/sdk",
        "@notionhq/notion-mcp-server"
    ]
    
    success = True
    for package in node_packages:
        if not run_command(["npm", "install", "-g", package], f"Installing {package}"):
            print(f"⚠️  Failed to install {package} (will use mock responses)")
            # Don't fail for optional Node packages
    
    return success

def verify_installation():
    """Verify that key packages are installed correctly."""
    print("\n✅ Verifying Installation...")
    
    test_imports = [
        ("dotenv", "python-dotenv"),
        ("click", "click"),
        ("httpx", "httpx"),
        ("streamlit", "streamlit"),
        ("fastapi", "fastapi"),
        ("pydantic", "pydantic"),
    ]
    
    all_good = True
    for module, package in test_imports:
        try:
            __import__(module)
            print(f"  ✅ {package}: OK")
        except ImportError:
            print(f"  ❌ {package}: Failed to import")
            all_good = False
    
    # Test optional imports
    optional_imports = [
        ("google.adk", "google-adk"),
        ("a2a", "a2a-sdk"),
        ("litellm", "litellm"),
        ("mcp", "mcp"),
    ]
    
    for module, package in optional_imports:
        try:
            __import__(module)
            print(f"  ✅ {package}: OK")
        except ImportError:
            print(f"  ⚠️  {package}: Not available (some features may not work)")
    
    return all_good

def create_basic_config():
    """Create basic configuration if needed."""
    print("\n⚙️  Setting up basic configuration...")
    
    # Check if .env exists
    if not Path(".env").exists() and Path(".env.example").exists():
        import shutil
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from .env.example")
        print("📝 Please edit .env file with your API keys")
    elif Path(".env").exists():
        print("✅ .env file already exists")
    else:
        # Create a basic .env file
        basic_env = '''# ADK A2A Gemini Configuration
# Replace with your actual API keys

GOOGLE_API_KEY=your_google_api_key_here
NOTION_API_KEY=secret_your_notion_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Agent Ports (defaults)
NOTION_AGENT_PORT=8002
ELEVENLABS_AGENT_PORT=8003
HOST_AGENT_PORT=8001

# UI Configuration
UI_PORT=8080
LOG_LEVEL=INFO
'''
        Path(".env").write_text(basic_env)
        print("✅ Created basic .env file")
        print("📝 Please edit .env file with your actual API keys")

def main():
    """Main installation function."""
    print("🚀 ADK A2A Gemini Project - Dependency Installation")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required. Current version:", sys.version)
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")
    
    # Installation steps
    steps = [
        ("Upgrading pip", upgrade_pip),
        ("Installing core dependencies", install_core_dependencies),
        ("Installing ML dependencies", install_ml_dependencies),
        ("Installing web dependencies", install_web_dependencies),
        ("Installing ADK dependencies", install_adk_dependencies),
        ("Installing MCP dependencies", install_mcp_dependencies),
        ("Installing development dependencies", install_dev_dependencies),
        ("Installing Node.js dependencies", install_node_dependencies),
        ("Verifying installation", verify_installation),
        ("Setting up configuration", create_basic_config),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        try:
            if step_func():
                success_count += 1
            else:
                print(f"⚠️  {step_name} had issues (continuing anyway)")
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Installation Summary: {success_count}/{len(steps)} steps completed successfully")
    
    if success_count >= 7:  # Core dependencies installed
        print("\n🎉 Installation completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Edit .env file with your API keys:")
        print("   - GOOGLE_API_KEY (for Gemini)")
        print("   - NOTION_API_KEY (for Notion integration)")
        print("   - ELEVENLABS_API_KEY (for text-to-speech)")
        print("2. Test the setup: python scripts/test_setup.py")
        print("3. Start the agents: python scripts/start_agents.py")
        print("4. Launch UI: streamlit run ui/streamlit_app.py --server.port 8080")
    else:
        print(f"\n⚠️  Installation completed with issues.")
        print("Some features may not work correctly.")
        print("Try running individual pip install commands for failed packages.")

if __name__ == "__main__":
    main()