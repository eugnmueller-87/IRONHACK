# LAB 4 — Using MCP in LangChain

A LangChain document-analysis agent that connects to a local filesystem via MCP
(Model Context Protocol), demonstrating standardised tool integration across Steps 1-8
of the lab brief.

## File Map

| Path | Purpose |
|------|---------|
| `mcp_langchain.py` | Main script — MCP client setup, tool loading, agent, demo queries, direct-API comparison |
| `documents/` | Sample text files the agent reads during the demo |
| `documents/ai_trends_2025.txt` | AI industry trends document |
| `documents/mcp_overview.txt` | MCP concepts reference |
| `documents/langchain_agents.txt` | LangChain agents quick-reference |
| `lab_summary.md` | Required narrative — MCP vs direct API trade-offs |
| `.env` | OpenAI API key (not committed to git) |

## Prerequisites

- Python 3.10+
- Node.js 18+ (for `npx @modelcontextprotocol/server-filesystem`)
- OpenAI API key

## Setup

```bash
# 1. Install Python dependencies
pip install langchain langchain-openai langchain-mcp-adapters mcp python-dotenv

# 2. Confirm Node is available (MCP server uses npx)
node --version

# 3. Add your key to .env
#    OPENAI_API_KEY=sk-...
```

## Run

```bash
python mcp_langchain.py
```

The script will:
1. Spin up a local filesystem MCP server pointing at `./documents/`
2. Print all discovered MCP tools
3. Run 4 demo queries through a LangChain tool-calling agent
4. Run a direct-API comparison query (no MCP) for contrast

## What Each Step Covers

| Lab Step | Where in code |
|----------|--------------|
| Step 1 — Setup | `load_dotenv`, imports |
| Step 2 — Connect MCP | `MultiServerMCPClient(server_config)` |
| Step 3 — Load tools | `get_mcp_tools()` |
| Step 4 — Create agent | `build_agent()` |
| Step 5 — MCP resources | `print_resource_note()` + tool calls |
| Step 6 — Complete agent | `run_demo()` with 4 real queries |
| Step 7 — Direct API compare | `direct_api_demo()` |
| Step 8 — Practical example | Document analysis queries in `run_demo()` |
