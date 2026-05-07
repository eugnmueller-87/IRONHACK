# LAB 2 — NormalObjects Creative Complaint Handler (LangChain)

A creative AI agent that handles complaints about inconsistencies in the Normal Objects
universe using LangChain's tool-calling framework.

## Files

| File | Purpose |
|---|---|
| `normalobjects_langchain.py` | Main agent implementation |
| `lab_summary.md` | Short analysis paragraph (submission requirement) |
| `.env` | API key config (not committed — add your own key) |

## Setup

```bash
# 1. Install dependencies
pip install langchain langchain-openai python-dotenv

# 2. Add your OpenAI key to .env
#    OPENAI_API_KEY=sk-...

# 3. Run
python normalobjects_langchain.py
```

## Tools

| Tool | Description |
|---|---|
| `consult_demogorgon` | Get a chaotic Upside-Down perspective |
| `check_hawkins_records` | Look up historical Hawkins records |
| `cast_interdimensional_spell` | Suggest creative interdimensional fixes |
| `gather_party_wisdom` | Ask Mike, Dustin, Lucas & Will for advice |

## Notes

- Uses `langgraph.prebuilt.create_react_agent` (modern replacement for the deprecated
  `AgentExecutor` + `create_openai_tools_agent` pattern removed in LangChain 1.2+)
- The agent decides tool order freely — no fixed execution graph
