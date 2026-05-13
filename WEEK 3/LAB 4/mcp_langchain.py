"""
MCP + LangChain Integration Lab
================================
Connects to a local filesystem MCP server, loads its tools into LangChain,
and runs a document-analysis agent that reads files from ./documents/.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DOCS_DIR = str(Path(__file__).parent / "documents")


# ---------------------------------------------------------------------------
# Step 2 & 3 — Connect to MCP server and load tools
# ---------------------------------------------------------------------------
async def get_mcp_tools(client: MultiServerMCPClient):
    """Return LangChain-compatible tools from all connected MCP servers."""
    tools = await client.get_tools()
    print(f"\n[MCP] Loaded {len(tools)} tool(s):")
    for t in tools:
        print(f"  • {t.name}: {t.description[:80]}")
    return tools


# ---------------------------------------------------------------------------
# Step 5 — List MCP resources (informational, no adapter needed for stdio)
# ---------------------------------------------------------------------------
def print_resource_note():
    print(
        "\n[MCP Resources] The filesystem server exposes directory listings as "
        "resources. With a stdio server the adapter surfaces these through the "
        "read_file / list_directory tools rather than a separate resource URI, "
        "so we access them via tool calls in the agent below."
    )


# ---------------------------------------------------------------------------
# Step 4 & 6 — Build and run the agent
# ---------------------------------------------------------------------------
def build_agent(llm: ChatOpenAI, tools: list):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a helpful document-analysis assistant. "
                    "You have access to a filesystem MCP server that lets you "
                    "list directories and read files. "
                    "Always use the available tools to look up real file content "
                    "before answering questions about documents. "
                    "The documents live in: {docs_dir}"
                ),
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


async def run_demo(executor: AgentExecutor):
    queries = [
        "List all files available in the documents directory.",
        "Read the file about MCP and give me a one-paragraph summary.",
        "What are the top 3 AI trends mentioned in the ai_trends_2025 document?",
        "Compare the content of all three documents and tell me the common theme.",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print("=" * 60)
        result = await executor.ainvoke(
            {"input": query, "docs_dir": DOCS_DIR}
        )
        print(f"\nAgent Answer:\n{result['output']}")


# ---------------------------------------------------------------------------
# Step 7 — Direct API comparison (synchronous, no MCP)
# ---------------------------------------------------------------------------
def direct_api_demo(llm: ChatOpenAI):
    """Read a file directly in Python and pass content to the LLM — no MCP."""
    print("\n" + "=" * 60)
    print("DIRECT API COMPARISON (no MCP)")
    print("=" * 60)

    file_path = Path(DOCS_DIR) / "mcp_overview.txt"
    content = file_path.read_text(encoding="utf-8")

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer based on the document provided.",
        },
        {
            "role": "user",
            "content": f"Document:\n{content}\n\nQuestion: What problem does MCP solve?",
        },
    ]

    response = llm.invoke(messages)
    print(f"\nDirect API Answer:\n{response.content}")
    print(
        "\n[Comparison] Direct API: simple, fast, but requires manual file I/O "
        "and custom code for every data source. MCP: the agent discovers and "
        "calls tools dynamically — no manual plumbing needed per integration."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set. Check your .env file.")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)

    # MCP server config — filesystem server via npx (requires Node.js)
    server_config = {
        "filesystem": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                DOCS_DIR,
            ],
            "transport": "stdio",
        }
    }

    print(f"\n[Setup] Connecting to filesystem MCP server at: {DOCS_DIR}")

    async with MultiServerMCPClient(server_config) as client:
        # Step 2 & 3: connect and load tools
        tools = await get_mcp_tools(client)

        # Step 5: note on resources
        print_resource_note()

        # Step 4 & 6: build agent and run demo queries
        executor = build_agent(llm, tools)
        await run_demo(executor)

    # Step 7: direct API comparison (outside MCP context)
    direct_api_demo(llm)

    print("\n[Done] Lab complete.")


if __name__ == "__main__":
    asyncio.run(main())
