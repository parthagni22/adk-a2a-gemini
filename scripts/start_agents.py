#!/usr/bin/env python3
"""Start all agents for the ADK A2A Gemini project."""

import asyncio
import subprocess
import sys
import time
import signal
from pathlib import Path
from typing import Dict, List, Optional
import httpx
import click

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import config

class AgentManager:
    """Manages the lifecycle of all agents."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.agent_configs = {
            "notion": {
                "module": "agents.notion_agent",
                "port": config.NOTION_AGENT_PORT,
                "host": "localhost",
                "name": "Notion Agent"
            },
            "elevenlabs": {
                "module": "agents.elevenlabs_agent", 
                "port": config.ELEVENLABS_AGENT_PORT,
                "host": "localhost",
                "name": "ElevenLabs Agent"
            },
            "host": {
                "module": "agents.host_agent",
                "port": config.HOST_AGENT_PORT,
                "host": "localhost", 
                "name": "Host Agent"
            }
        }
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
    
    def start_agent(self, agent_key: str) -> bool:
        """Start a single agent."""
        if agent_key in self.processes:
            print(f"⚠️  {agent_key} agent is already running")
            return True
        
        agent_config = self.agent_configs[agent_key]
        cmd = [
            sys.executable, "-m", agent_config["module"],
            "--host", agent_config["host"],
            "--port", str(agent_config["port"])
        ]
        
        print(f"🚀 Starting {agent_config['name']} on port {agent_config['port']}")
        print(f"   Command: {' '.join(cmd)}")
        
        # Setup log files
        stdout_log = self.logs_dir / f"{agent_key}_agent_stdout.log"
        stderr_log = self.logs_dir / f"{agent_key}_agent_stderr.log"
        
        try:
            with open(stdout_log, 'w') as stdout_file, open(stderr_log, 'w') as stderr_file:
                process = subprocess.Popen(
                    cmd,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    text=True,
                    cwd=project_root
                )
                self.processes[agent_key] = process
                print(f"   ✅ Started with PID {process.pid}")
                print(f"   📋 Logs: {stdout_log} & {stderr_log}")
                return True
                
        except Exception as e:
            print(f"   ❌ Failed to start: {e}")
            return False
    
    async def wait_for_agent_ready(self, agent_key: str, timeout: int = 30) -> bool:
        """Wait for an agent to be ready."""
        agent_config = self.agent_configs[agent_key]
        url = f"http://{agent_config['host']}:{agent_config['port']}/.well-known/agent.json"
        
        print(f"⏳ Waiting for {agent_config['name']} to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(url)
                    if response.status_code == 200:
                        print(f"   ✅ {agent_config['name']} is ready!")
                        return True
            except (httpx.ConnectError, httpx.TimeoutException):
                await asyncio.sleep(1)
        
        print(f"   ❌ {agent_config['name']} failed to start within {timeout}s")
        return False
    
    def stop_agent(self, agent_key: str):
        """Stop a single agent."""
        if agent_key not in self.processes:
            return
        
        process = self.processes[agent_key]
        agent_name = self.agent_configs[agent_key]["name"]
        
        if process.poll() is None:  # Still running
            print(f"🛑 Stopping {agent_name} (PID: {process.pid})")
            process.terminate()
            
            try:
                process.wait(timeout=5)
                print(f"   ✅ {agent_name} stopped gracefully")
            except subprocess.TimeoutExpired:
                print(f"   ⚠️  {agent_name} didn't stop gracefully, killing...")
                process.kill()
                process.wait()
                print(f"   ✅ {agent_name} killed")
        
        del self.processes[agent_key]
    
    def stop_all_agents(self):
        """Stop all running agents."""
        print("\n🛑 Stopping all agents...")
        for agent_key in list(self.processes.keys()):
            self.stop_agent(agent_key)
        print("✅ All agents stopped")
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get the status of all agents."""
        status = {}
        for agent_key, config in self.agent_configs.items():
            if agent_key in self.processes:
                process = self.processes[agent_key]
                if process.poll() is None:
                    status[agent_key] = f"Running (PID: {process.pid})"
                else:
                    status[agent_key] = f"Stopped (Exit code: {process.poll()})"
            else:
                status[agent_key] = "Not started"
        return status

@click.command()
@click.option(
    "--agents",
    default="all",
    help="Comma-separated list of agents to start (notion,elevenlabs,host) or 'all'",
)
@click.option(
    "--timeout",
    default=30,
    type=int,
    help="Timeout in seconds to wait for agents to start",
)
@click.option(
    "--no-wait",
    is_flag=True,
    help="Don't wait for agents to be ready",
)
def main(agents: str, timeout: int, no_wait: bool):
    """Start ADK A2A agents."""
    print("🚀 ADK A2A Gemini Agent Starter")
    print("=" * 50)
    
    # Initialize agent manager
    manager = AgentManager()
    
    # Determine which agents to start
    if agents.lower() == "all":
        agents_to_start = ["notion", "elevenlabs", "host"]
    else:
        agents_to_start = [agent.strip() for agent in agents.split(",")]
    
    # Validate agent names
    invalid_agents = [agent for agent in agents_to_start if agent not in manager.agent_configs]
    if invalid_agents:
        print(f"❌ Invalid agent names: {invalid_agents}")
        print(f"Available agents: {list(manager.agent_configs.keys())}")
        return
    
    # Start agents
    started_agents = []
    for agent_key in agents_to_start:
        if manager.start_agent(agent_key):
            started_agents.append(agent_key)
        else:
            print(f"❌ Failed to start {agent_key} agent")
    
    if not started_agents:
        print("❌ No agents started successfully")
        return
    
    # Wait for agents to be ready (unless --no-wait)
    async def wait_for_agents():
        if no_wait:
            print("⏭️  Skipping readiness check (--no-wait specified)")
            return True
        
        print(f"\n⏳ Waiting for {len(started_agents)} agent(s) to be ready...")
        tasks = []
        for agent_key in started_agents:
            tasks.append(manager.wait_for_agent_ready(agent_key, timeout))
        
        results = await asyncio.gather(*tasks)
        return all(results)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n📡 Received signal {signum}")
        manager.stop_all_agents()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Wait for agents to be ready
        all_ready = asyncio.run(wait_for_agents())
        
        if all_ready or no_wait:
            print("\n🎉 Agents are running!")
            print("\n📊 Agent Status:")
            status = manager.get_agent_status()
            for agent_key, agent_status in status.items():
                if agent_key in started_agents:
                    print(f"   ✅ {manager.agent_configs[agent_key]['name']}: {agent_status}")
            
            print("\n📋 Next Steps:")
            print("1. Open a new terminal")
            print("2. Run: streamlit run ui/streamlit_app.py --server.port 8080")
            print("3. Open http://localhost:8080 in your browser")
            print("\n💡 Tips:")
            print("- Check logs in the 'logs/' directory if there are issues")
            print("- Press Ctrl+C to stop all agents")
            
            # Keep running until interrupted
            print("\n⏳ Agents running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
                
                # Check if any agent died
                for agent_key in started_agents:
                    if agent_key in manager.processes:
                        process = manager.processes[agent_key]
                        if process.poll() is not None:  # Process died
                            print(f"\n❌ {manager.agent_configs[agent_key]['name']} died unexpectedly")
                            print(f"   Exit code: {process.poll()}")
                            print(f"   Check logs: logs/{agent_key}_agent_stderr.log")
        else:
            print("\n❌ One or more agents failed to start")
            print("📋 Troubleshooting:")
            print("1. Check the log files in the 'logs/' directory")
            print("2. Ensure all dependencies are installed: python scripts/install_deps.py")
            print("3. Verify your .env file has valid API keys")
            print("4. Run tests: python scripts/test_setup.py")
            
    except KeyboardInterrupt:
        print("\n📡 Received interrupt signal")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        manager.stop_all_agents()

if __name__ == "__main__":
    main()