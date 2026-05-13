import argparse
import os
import sys

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient

APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
SERVERS_DIR = os.path.join(ROOT_DIR, "mcp_servers")

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(SERVERS_DIR, "general_server.py")]
    )
))

agent = Agent(tools=[mcp_client])

parser = argparse.ArgumentParser(description="Ask the general tools agent a one-shot question")
parser.add_argument("prompt", help="Question to ask, for example: 'What is 25 * 4?' ")
args = parser.parse_args()

agent(args.prompt)

