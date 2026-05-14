# multi_mcp_strands

Multi-agent demo using Strands Agents with multiple MCP servers over stdio.

## Folder structure

```text
multi_mcp_strands/
├── app/
│   ├── general_chat_cli.py
│   ├── multi_agent_cli.py
│   └── single_prompt_cli.py
├── mcp_servers/
│   ├── general_server.py
│   ├── salary_server.py
│   ├── time_server.py
│   └── weather_server.py
├── pyproject.toml
├── README.md
└── uv.lock
```

## Components

- `app/single_prompt_cli.py` — one-shot CLI using the general MCP server
- `app/general_chat_cli.py` — interactive single-agent chat using the general MCP server
- `app/multi_agent_cli.py` — orchestrator agent with direct MCP clients (general, time, weather, salary, optional Atlassian)
- `mcp_servers/general_server.py` — calculator, string utilities, key-value tools
- `mcp_servers/time_server.py` — current time, world clock, timezone difference, unix timestamp
- `mcp_servers/weather_server.py` — current weather and forecast
- `mcp_servers/salary_server.py` — salary breakup, tax, hike, offer comparison

## Install

```bash
cd /Users/rajupatil/Projects/AgenticAI/multi_mcp_strands
uv venv --python 3.13
source .venv/bin/activate
uv sync
```

## Run

One-shot prompt:

```bash
python app/single_prompt_cli.py "What is 25 * 4?"
```

Single-agent chat:

```bash
python app/general_chat_cli.py
```

Multi-agent router:

```bash
python app/multi_agent_cli.py
```

Optional: enable external Atlassian MCP server in the same orchestrator:

```bash
export ATLASSIAN_MCP_COMMAND="npx"
export ATLASSIAN_MCP_ARGS="-y <your-atlassian-mcp-package-or-entrypoint>"
export ATLASSIAN_BASE_URL="https://your-domain.atlassian.net"
export ATLASSIAN_EMAIL="you@example.com"
export ATLASSIAN_API_TOKEN="<token>"
python app/multi_agent_cli.py
```

## Example prompts

```text
What is 25 * 4?
What time is it in Asia/Kolkata?
What is the weather in Pune?
Calculate salary breakup for 18 LPA
Cau you please get details of jira ticket ADLBUGS-673
Create a Confluence page in space " RajuConfluence " with title "MDR SLA Enforcement Lambda – Code Walkthrough" and body "<p>Initial draft.</p>". Return page id and URL.
Get a Confluence page in space " RajuConfluence " with title "MDR SLA Enforcement Lambda – Code Walkthrough". Return page id and URL.
```

