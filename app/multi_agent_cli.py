import os
import sys

from dotenv import load_dotenv
from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── Shared LLM Model ──────────────────────────────────────────────────────────
model = BedrockModel(model_id="us.amazon.nova-lite-v1:0")

APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
SERVERS_DIR = os.path.join(ROOT_DIR, "mcp_servers")

def local_mcp_client(server_file: str) -> MCPClient:
    """Create an MCP client for a local Python MCP server file."""
    return MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command=sys.executable,
            args=[os.path.join(SERVERS_DIR, server_file)],
        )
    ))


# ── MCP Client 1: General Tools (calculator, string, datetime, kv-store) ──────
mcp_general = local_mcp_client("general_server.py")

# ── MCP Client 2: Time Tools ──────────────────────────────────────────────────
mcp_time = local_mcp_client("time_server.py")

# ── MCP Client 3: Weather Tools ───────────────────────────────────────────
mcp_weather = local_mcp_client("weather_server.py")

# ── MCP Client 4: Salary & HR Tools ───────────────────────────────────────────
mcp_salary = local_mcp_client("salary_server.py")

# ── Optional MCP Client 5: Atlassian Confluence + Jira via mcp-atlassian ──────
# Reads credentials from .env automatically (loaded above).
# Install the server once: pip install mcp-atlassian
# Or run via uvx (no install needed): command="uvx", args=["mcp-atlassian"]
confluence_url = os.getenv("CONFLUENCE_URL", "").strip()
confluence_user = os.getenv("CONFLUENCE_USERNAME", "").strip()
confluence_token = os.getenv("CONFLUENCE_API_TOKEN", "").strip()
jira_url = os.getenv("JIRA_URL", "").strip()
jira_user = os.getenv("JIRA_USERNAME", "").strip()
jira_token = os.getenv("JIRA_API_TOKEN", "").strip()

mcp_atlassian = None
if confluence_url and confluence_user and confluence_token:
    mcp_atlassian = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["mcp-atlassian"],
            env=dict(os.environ) | {
                "CONFLUENCE_URL": confluence_url,
                "CONFLUENCE_USERNAME": confluence_user,
                "CONFLUENCE_API_TOKEN": confluence_token,
                "JIRA_URL": jira_url,
                "JIRA_USERNAME": jira_user,
                "JIRA_API_TOKEN": jira_token,
            },
        )
    ))

tool_clients = [mcp_general, mcp_time, mcp_weather, mcp_salary]
if mcp_atlassian is not None:
    tool_clients.append(mcp_atlassian)

# ── Orchestrator ───────────────────────────────────────────
# Single orchestrator with direct access to all MCP tools.
# This avoids nested agent/tool wrapping that can print "Routing to ..." messages.
orchestrator = Agent(
    model=model,
    tools=tool_clients,
    system_prompt=(
        "You are an orchestrator assistant with tools from MCP servers: "
        "general, time, weather, salary, and optionally Atlassian Confluence/Jira (if configured). "
        "For user requests, call the appropriate tool and return only the final answer. "
        "Do not narrate internal routing or mention tool names. "
        "For wiki/Confluence queries use confluence tools to get or post pages. "
        "If the user sends a greeting like 'hi'/'hello', reply briefly and ask what they need."
    ),
)


# ── Interactive Chat Loop ──────────────────────────────────────────────────────
print("=" * 60)
print("🤖 Multi-Agent System Ready!")
print("=" * 60)
print("  Orchestrator   → LLM-based routing to specialist agents")
print("  Time Agent     → current time/date/timezone")
print("  Weather Agent  → current weather and forecast")
print("  General Agent  → calculator, strings, kv-store")
print("  Salary Agent   → salary breakup, tax, hike, offer compare")
if mcp_atlassian is not None:
    print("  Atlassian MCP  → external Jira/Confluence tools")
print("=" * 60)
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if not user_input:
        continue

    if user_input.lower() == "exit":
        print("Goodbye! 👋")
        break

    print("\n🤖 Orchestrator is routing your query...\n")
    orchestrator(user_input)
    print("\n")
