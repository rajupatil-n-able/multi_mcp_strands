import os
import sys

from dotenv import load_dotenv
from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
SERVERS_DIR = os.path.join(ROOT_DIR, "mcp_servers")

# ── Model factory: each agent gets its own instance ───────────────────────────
# Sharing one BedrockModel across agents is unsafe in concurrent scenarios.
def make_model() -> BedrockModel:
    return BedrockModel(model_id="us.amazon.nova-lite-v1:0")


def local_mcp_client(server_file: str) -> MCPClient:
    """Create an MCP client for a local Python MCP server file (stdio transport)."""
    return MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command=sys.executable,
            args=[os.path.join(SERVERS_DIR, server_file)],
        )
    ))


# ── Specialist Agents — each owns its model + MCP client ──────────────────────

general_agent = Agent(
    model=make_model(),
    tools=[local_mcp_client("general_server.py")],
    callback_handler=None,   # silent — orchestrator prints final answer
    system_prompt=(
        "You are a general-purpose assistant. "
        "You can perform calculations, string operations, and use a key-value store. "
        "Return only the final answer, no internal commentary."
    ),
)

time_agent = Agent(
    model=make_model(),
    tools=[local_mcp_client("time_server.py")],
    callback_handler=None,
    system_prompt=(
        "You are a time and timezone specialist. "
        "You can return current time, world clock, timezone differences, and unix timestamps. "
        "Return only the final answer."
    ),
)

weather_agent = Agent(
    model=make_model(),
    tools=[local_mcp_client("weather_server.py")],
    callback_handler=None,
    system_prompt=(
        "You are a weather specialist. "
        "You can provide current weather and forecasts for any city. "
        "Return only the final answer."
    ),
)

salary_agent = Agent(
    model=make_model(),
    tools=[local_mcp_client("salary_server.py")],
    callback_handler=None,
    system_prompt=(
        "You are a salary and HR specialist. "
        "You can calculate salary breakup, tax, hike percentages, and compare offers. "
        "Return only the final answer."
    ),
)

# ── Optional Atlassian Agent ───────────────────────────────────────────────────
confluence_url   = os.getenv("CONFLUENCE_URL",      os.getenv("ATLASSIAN_BASE_URL",   "")).strip()
confluence_user  = os.getenv("CONFLUENCE_USERNAME", os.getenv("ATLASSIAN_EMAIL",      "")).strip()
confluence_token = os.getenv("CONFLUENCE_API_TOKEN",os.getenv("ATLASSIAN_API_TOKEN",  "")).strip()
jira_url         = os.getenv("JIRA_URL",            os.getenv("ATLASSIAN_BASE_URL",   "")).strip()
jira_user        = os.getenv("JIRA_USERNAME",       os.getenv("ATLASSIAN_EMAIL",      "")).strip()
jira_token       = os.getenv("JIRA_API_TOKEN",      os.getenv("ATLASSIAN_API_TOKEN",  "")).strip()

_atlassian_ready = (confluence_url and confluence_user and confluence_token) or \
                   (jira_url and jira_user and jira_token)

atlassian_agent: Agent | None = None
if _atlassian_ready:
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
    atlassian_agent = Agent(
        model=make_model(),
        tools=[mcp_atlassian],
        callback_handler=None,
        system_prompt=(
            "You are an Atlassian specialist with access to Confluence and Jira. "
            "You can fetch Jira tickets, create/update issues, and read/write Confluence pages. "
            "Return only the final answer."
        ),
    )


# ── Wrap Each Specialist Agent as an Orchestrator Tool ────────────────────────
# Use result.message for clean text output from AgentResult (not str() which may include metadata).

@tool
def general_tool(query: str) -> str:
    """
    Use for general calculations, arithmetic, string operations,
    and key-value store queries. Examples: 'What is 25 * 4?', 'Uppercase hello'.
    """
    return general_agent(query).message


@tool
def time_tool(query: str) -> str:
    """
    Use for time and timezone queries.
    Examples: 'What time is it in Tokyo?', 'Current UTC time', 'Unix timestamp now'.
    """
    return time_agent(query).message


@tool
def weather_tool(query: str) -> str:
    """
    Use for weather queries.
    Examples: 'What is the weather in Pune?', 'Forecast for London'.
    """
    return weather_agent(query).message


@tool
def salary_tool(query: str) -> str:
    """
    Use for salary, HR, and compensation queries.
    Examples: 'Calculate salary breakup for 18 LPA', 'Compare two offers', 'Tax on 25 LPA'.
    """
    return salary_agent(query).message


@tool
def atlassian_tool(query: str) -> str:
    """
    Use for Atlassian Jira and Confluence queries.
    Examples: 'Get Jira ticket PROJ-123', 'Search Confluence for onboarding guide'.
    Only available when Atlassian credentials are configured in .env.
    """
    if atlassian_agent is None:
        return "Atlassian is not configured. Set CONFLUENCE_URL/JIRA_URL credentials in .env."
    return atlassian_agent(query).message


# ── Orchestrator ───────────────────────────────────────────────────────────────
orchestrator = Agent(
    model=make_model(),
    tools=[general_tool, time_tool, weather_tool, salary_tool, atlassian_tool],
    system_prompt=(
        "You are an orchestrator assistant. Route each user request to the correct specialist tool:\n"
        "- general_tool   → calculations, strings, kv-store\n"
        "- time_tool      → current time, timezones, world clock\n"
        "- weather_tool   → weather and forecasts\n"
        "- salary_tool    → salary breakup, tax, hike, offer comparison\n"
        "- atlassian_tool → Jira tickets, Confluence pages\n\n"
        "Call the tool with the user's original query. "
        "Return only the specialist's answer — no routing commentary, no tool names. "
        "If the user sends a greeting like 'hi'/'hello', reply briefly and ask what they need."
    ),
)


# ── Interactive Chat Loop ──────────────────────────────────────────────────────
print("=" * 60)
print("🤖 Multi-Agent System Ready!")
print("=" * 60)
print("  Orchestrator    → LLM routes to specialist agents")
print("    ├── General Agent   → calculator, strings, kv-store")
print("    ├── Time Agent      → current time / timezones")
print("    ├── Weather Agent   → weather and forecasts")
print("    ├── Salary Agent    → salary breakup, tax, hike")
print("    └── Atlassian Agent → Jira / Confluence", "(✅ active)" if atlassian_agent else "(⚠️  not configured)")
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
