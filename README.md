# ADK A2A Gemini Project

A complete multi-agent system built with Google's Agent Development Kit (ADK) that demonstrates Agent-to-Agent (A2A) communication patterns. The system integrates Notion for information retrieval and ElevenLabs for text-to-speech conversion, all powered by Google's Gemini models.

## 🚀 Features

- **Multi-Agent Architecture**: Orchestrated system with specialized agents
- **A2A Communication**: Agents communicate via standardized A2A protocol
- **Notion Integration**: Search workspaces and query databases
- **Text-to-Speech**: Convert text to audio using ElevenLabs
- **Web UI**: Beautiful Streamlit interface for interaction
- **Error Handling**: Robust error handling with fallback responses
- **Docker Ready**: Easy deployment with containerization support

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   Host Agent    │    │ Child Agents    │
│                 │◄──►│ (Orchestrator)  │◄──►│ - Notion        │
│ - Chat Interface│    │                 │    │ - ElevenLabs    │
│ - Agent Status  │    │ - Task Routing  │    │                 │
└─────────────────┘    │ - Response Sync │    └─────────────────┘
                       └─────────────────┘
```

### Agent Roles

- **Host Agent**: Master orchestrator that routes tasks and synthesizes responses
- **Notion Agent**: Specialized for workspace search and database queries
- **ElevenLabs Agent**: Focused on text-to-speech conversion

## 📋 Prerequisites

- **Python 3.11+** 
- **Node.js 16+** (for MCP servers)
- **API Keys**:
  - Google API Key (for Gemini)
  - Notion API Key
  - ElevenLabs API Key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Create project directory
mkdir adk-a2a-gemini
cd adk-a2a-gemini

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Create Project Files

Copy all the files from the artifacts into your project directory following the structure shown in the first artifact.

### 3. Install Dependencies

```bash
# Run the automated installer
python scripts/install_deps.py

# Or install manually:
pip install -r requirements.txt
npm install -g @notionhq/notion-mcp-server @modelcontextprotocol/sdk
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# GOOGLE_API_KEY=your_google_api_key_here
# NOTION_API_KEY=secret_your_notion_api_key_here  
# ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

### 5. Test Setup

```bash
# Verify everything is working
python scripts/test_setup.py
```

### 6. Start the System

```bash
# Terminal 1: Start all agents
python scripts/start_agents.py

# Terminal 2: Launch UI
streamlit run ui/streamlit_app.py --server.port 8080
```

### 7. Open in Browser

Visit http://localhost:8080 to interact with your multi-agent system!

## 💬 Example Interactions

Try these example queries in the UI:

### Simple Queries
- `"Search my Notion workspace for 'project documentation'"`
- `"Convert this text to speech: 'Hello from ADK A2A!'"`
- `"Count how many entries are in the 'Sermon Notes' database"`

### Multi-Agent Workflows
- `"Find my meeting notes and read the summary aloud"`
- `"Search for project updates and convert the results to speech"`
- `"Count database entries and announce the total"`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google API key for Gemini | ✅ Yes |
| `NOTION_API_KEY` | Notion integration token | ✅ Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | ✅ Yes |
| `NOTION_AGENT_PORT` | Port for Notion agent | ❌ No (8002) |
| `ELEVENLABS_AGENT_PORT` | Port for ElevenLabs agent | ❌ No (8003) |
| `HOST_AGENT_PORT` | Port for Host agent | ❌ No (8001) |
| `UI_PORT` | Port for Streamlit UI | ❌ No (8080) |
| `LOG_LEVEL` | Logging level | ❌ No (INFO) |

### Notion Setup

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Copy the "Internal Integration Token"
3. Share your Notion pages/databases with the integration

### ElevenLabs Setup

1. Sign up at https://elevenlabs.io/
2. Get your API key from the profile settings
3. Note: Current implementation includes mock responses for development

## 🛠️ Development

### Project Structure

```
adk-a2a-gemini/
├── agents/                 # All agent implementations
│   ├── notion_agent/      # Notion workspace agent
│   ├── elevenlabs_agent/  # Text-to-speech agent
│   └── host_agent/        # Orchestrator agent
├── core/                  # Core utilities and tools
├── ui/                    # Streamlit user interface
├── scripts/               # Setup and utility scripts
├── tests/                 # Test suite
└── logs/                  # Agent logs (auto-created)
```

### Running Individual Agents

```bash
# Start agents individually for debugging
python -m agents.notion_agent --port 8002
python -m agents.elevenlabs_agent --port 8003  
python -m agents.host_agent --port 8001
```

### Testing

```bash
# Run all tests
python scripts/test_setup.py

# Run specific tests
python -m pytest tests/

# Test individual agents
python -m pytest tests/test_agents.py -v
```

### Logging

Logs are saved to the `logs/` directory:
- `notion_agent_stdout.log` / `notion_agent_stderr.log`
- `elevenlabs_agent_stdout.log` / `elevenlabs_agent_stderr.log`
- `host_agent_stdout.log` / `host_agent_stderr.log`

### Adding New Agents

1. Create new agent directory in `agents/`
2. Implement agent class extending `BaseADKAgent`
3. Add executor class
4. Create `__main__.py` for A2A service
5. Update `config.py` and `start_agents.py`

## 🚨 Troubleshooting

### Common Issues

#### Agents Won't Start
```bash
# Check logs
cat logs/notion_agent_stderr.log

# Verify dependencies
python scripts/test_setup.py

# Check ports
netstat -an | grep 800[1-3]
```

#### API Key Issues
```bash
# Verify environment
python -c "import config; print(config.get_config_summary())"

# Check .env file
cat .env
```

#### MCP Connection Errors
- Ensure Node.js packages are installed globally
- Check that Notion integration has page access
- Verify API keys are correct

### Debug Mode

```bash
# Start with debug logging
export LOG_LEVEL=DEBUG
python scripts/start_agents.py

# Or start individual agents with verbose output
python -m agents.notion_agent --port 8002 --log-level DEBUG
```

## 🔄 Architecture Patterns

### A2A Communication

```python
# Host Agent delegates to child agents
result = delegate_task_sync(
    agent_name="notion_agent",
    task_description="Search workspace for 'project docs'"
)
```

### Mock vs Real MCP

The system includes both real MCP integration and mock responses:

- **Development**: Uses mock responses when MCP servers unavailable
- **Production**: Connects to real Notion/ElevenLabs MCP servers
- **Graceful Degradation**: Falls back to mocks on connection failure

## 🚀 Deployment

### Docker Support

```bash
# Build image
docker build -t adk-a2a-gemini .

# Run container
docker run -p 8080:8080 --env-file .env adk-a2a-gemini
```

### Cloud Deployment

1. **Environment Setup**: Ensure all API keys are configured
2. **Service Mesh**: Deploy each agent as a separate service
3. **Load Balancing**: Use reverse proxy for the UI
4. **Monitoring**: Set up logging and health checks

## 📚 API Reference

### Host Agent Tools

#### `delegate_task_sync(agent_name, task_description)`
Delegate tasks to specialized child agents.

**Parameters:**
- `agent_name`: `"notion_agent"` or `"elevenlabs_agent"`
- `task_description`: Detailed instruction for the child agent

### Agent Endpoints

Each agent exposes A2A-compliant endpoints:
- `GET /.well-known/agent.json` - Agent capability metadata
- `POST /v1/sessions/{sessionId}/turn` - Process user input
- `GET /v1/sessions/{sessionId}/tasks/{taskId}` - Check task status

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google ADK Team** - For the excellent Agent Development Kit
- **Anthropic** - For A2A protocol specification
- **Notion Team** - For the powerful API and MCP server
- **ElevenLabs** - For high-quality text-to-speech technology

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/adk-a2a-gemini/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/adk-a2a-gemini/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/adk-a2a-gemini/wiki)

---

<div align="center">
  <strong>Built with ❤️ using Google ADK, A2A Protocol, and Gemini AI</strong>
</div>