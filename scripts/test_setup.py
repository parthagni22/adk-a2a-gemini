#!/usr/bin/env python3
"""Test setup and configuration for the ADK A2A Gemini project."""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports() -> Tuple[bool, List[str]]:
    """Test that all required packages can be imported."""
    print("🔍 Testing Package Imports...")
    
    packages = [
        ("google.adk", "Google ADK"),
        ("a2a", "A2A SDK"),
        ("streamlit", "Streamlit"),
        ("fastapi", "FastAPI"),
        ("httpx", "HTTPX"),
        ("dotenv", "Python Dotenv"),
        ("click", "Click"),
        ("litellm", "LiteLLM"),
        ("mcp", "MCP"),
        ("pydantic", "Pydantic"),
    ]
    
    results = []
    all_success = True
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✅ {name}: Successfully imported")
            results.append(f"✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: Failed to import - {e}")
            results.append(f"❌ {name}: {str(e)}")
            all_success = False
    
    return all_success, results

def test_configuration() -> Tuple[bool, Dict[str, Any]]:
    """Test configuration loading and validation."""
    print("\n🔍 Testing Configuration...")
    
    try:
        import config
        
        # Test configuration
        config_summary = config.get_config_summary()
        validation_errors = config.validate_config()
        
        print(f"  📊 Configuration Summary:")
        for key, value in config_summary.items():
            status = "✅" if value else "❌"
            print(f"    {status} {key}: {value}")
        
        if validation_errors:
            print(f"\n  ⚠️  Configuration Issues:")
            for error in validation_errors:
                print(f"    ❌ {error}")
            return False, {"errors": validation_errors, "summary": config_summary}
        else:
            print(f"  ✅ All required configuration set")
            return True, {"summary": config_summary}
            
    except Exception as e:
        print(f"  ❌ Configuration loading failed: {e}")
        return False, {"error": str(e)}

def test_agent_creation() -> Tuple[bool, List[str]]:
    """Test creating each agent."""
    print("\n🔍 Testing Agent Creation...")
    
    results = []
    all_success = True
    
    # Test Notion Agent
    try:
        from agents.notion_agent.agent import create_notion_agent
        agent = create_notion_agent()
        print(f"  ✅ Notion agent created successfully")
        results.append("✅ Notion Agent")
    except Exception as e:
        print(f"  ❌ Notion agent creation failed: {e}")
        results.append(f"❌ Notion Agent: {str(e)}")
        all_success = False
    
    # Test ElevenLabs Agent
    try:
        from agents.elevenlabs_agent.agent import create_elevenlabs_agent
        agent = create_elevenlabs_agent()
        print(f"  ✅ ElevenLabs agent created successfully")
        results.append("✅ ElevenLabs Agent")
    except Exception as e:
        print(f"  ❌ ElevenLabs agent creation failed: {e}")
        results.append(f"❌ ElevenLabs Agent: {str(e)}")
        all_success = False
    
    # Test Host Agent
    try:
        from agents.host_agent.agent import create_host_agent
        agent = create_host_agent()
        print(f"  ✅ Host agent created successfully")
        results.append("✅ Host Agent")
    except Exception as e:
        print(f"  ❌ Host agent creation failed: {e}")
        results.append(f"❌ Host Agent: {str(e)}")
        all_success = False
    
    return all_success, results

async def test_simple_workflow() -> Tuple[bool, str]:
    """Test a simple agent workflow."""
    print("\n🔍 Testing Simple Workflow...")
    
    try:
        from google.adk.agents import Agent
        from google.adk.models.lite_llm import LiteLlm
        from google.adk.runners import Runner
        from google.genai import types
        from google.adk.sessions import InMemorySessionService
        from google.adk.artifacts import InMemoryArtifactService
        from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
        import config
        
        # Create simple test agent
        test_agent = Agent(
            name="test_workflow_agent",
            model=LiteLlm(model="gemini/gemini-2.0-flash", api_key=config.GOOGLE_API_KEY),
            description="Simple test agent for workflow validation",
            instruction="You are a helpful test assistant. Respond briefly to user queries."
        )
        
        # Create services
        session_service = InMemorySessionService()
        artifact_service = InMemoryArtifactService()
        memory_service = InMemoryMemoryService()
        
        # Create runner with all required services
        runner = Runner(
            agent=test_agent,
            app_name="workflow_test",
            session_service=session_service,
            artifact_service=artifact_service,
            memory_service=memory_service
        )
        
        print("  🤖 Testing basic agent interaction...")
        
        # Create session first
        user_id = "test_user"
        session_id = "test_session"
        
        await session_service.create_session(
            app_name="workflow_test",
            user_id=user_id,
            session_id=session_id,
            state={}
        )
        
        # Test the workflow
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                role="user", 
                parts=[types.Part(text="Hello! Please respond with a simple greeting.")]
            )
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        response_text = part.text.strip()
                        print(f"  ✅ Agent responded: {response_text[:100]}...")
                        return True, response_text
        
        return False, "No response received"
        
    except Exception as e:
        print(f"  ❌ Workflow test failed: {e}")
        return False, str(e)

def test_file_structure() -> Tuple[bool, List[str]]:
    """Test that required files and directories exist."""
    print("\n🔍 Testing File Structure...")
    
    required_items = [
        ("config.py", "file"),
        ("agents", "directory"),
        ("agents/notion_agent", "directory"),
        ("agents/elevenlabs_agent", "directory"),
        ("agents/host_agent", "directory"),
        ("core", "directory"),
        ("ui", "directory"),
        ("scripts", "directory"),
        (".env", "file"),
        ("requirements.txt", "file"),
    ]
    
    results = []
    all_success = True
    
    for item, item_type in required_items:
        path = Path(item)
        if item_type == "file" and path.is_file():
            print(f"  ✅ {item}: File exists")
            results.append(f"✅ {item}")
        elif item_type == "directory" and path.is_dir():
            print(f"  ✅ {item}: Directory exists")
            results.append(f"✅ {item}")
        else:
            print(f"  ❌ {item}: {item_type.title()} missing")
            results.append(f"❌ {item}: Missing")
            all_success = False
    
    return all_success, results

def test_mcp_tools() -> Tuple[bool, List[str]]:
    """Test MCP tools functionality."""
    print("\n🔍 Testing MCP Tools...")
    
    results = []
    
    try:
        from core.mcp_tools import mcp_manager
        print("  ✅ MCP manager imported successfully")
        results.append("✅ MCP Manager Import")
        
        # Test tool creation
        notion_tool = mcp_manager.get_tool("notion")
        elevenlabs_tool = mcp_manager.get_tool("elevenlabs")
        
        if notion_tool:
            print("  ✅ Notion MCP tool available")
            results.append("✅ Notion MCP Tool")
        else:
            print("  ❌ Notion MCP tool not available")
            results.append("❌ Notion MCP Tool")
        
        if elevenlabs_tool:
            print("  ✅ ElevenLabs MCP tool available")
            results.append("✅ ElevenLabs MCP Tool")
        else:
            print("  ❌ ElevenLabs MCP tool not available")
            results.append("❌ ElevenLabs MCP Tool")
        
        return True, results
        
    except Exception as e:
        print(f"  ❌ MCP tools test failed: {e}")
        results.append(f"❌ MCP Tools: {str(e)}")
        return False, results

async def main():
    """Main test function."""
    print("🧪 ADK A2A Gemini Project Setup Test")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("File Structure", test_file_structure),
        ("Package Imports", test_imports),
        ("Configuration", test_configuration),
        ("MCP Tools", test_mcp_tools),
        ("Agent Creation", test_agent_creation),
        ("Simple Workflow", test_simple_workflow),
    ]
    
    results = {}
    overall_success = True
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                success, details = await test_func()
            else:
                success, details = test_func()
            
            results[test_name] = {"success": success, "details": details}
            if not success:
                overall_success = False
                
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = {"success": False, "details": str(e)}
            overall_success = False
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    passed = sum(1 for result in results.values() if result["success"])
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if overall_success:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\n📋 Next Steps:")
        print("1. Run: python scripts/start_agents.py")
        print("2. In another terminal: streamlit run ui/streamlit_app.py --server.port 8080")
        print("3. Open http://localhost:8080 in your browser")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("Please review the errors above and fix them before proceeding.")
        
        # Provide specific guidance
        if not results.get("Configuration", {}).get("success"):
            print("\n💡 Configuration Issues:")
            print("   - Make sure your .env file has valid API keys")
            print("   - Check that all required environment variables are set")

if __name__ == "__main__":
    asyncio.run(main())