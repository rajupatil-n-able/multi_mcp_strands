import sys
import os

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0"
)

APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
SERVERS_DIR = os.path.join(ROOT_DIR, "mcp_servers")

# Connect to our local custom MCP server
mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(SERVERS_DIR, "general_server.py")]
    )
))

# Inject MCP tools into the agent
agent = Agent(model=model, tools=[mcp_client])

print("🤖 Agent ready! Tools available: calculator, string_info, current_datetime, kv_set, kv_get, kv_list")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    agent(user_input)
    print("\n")
