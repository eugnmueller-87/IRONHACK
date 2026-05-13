# LAB 2 — NormalObjects Creative Complaint Handler

Welcome to the **Downside-Up Complaint Bureau**! This project builds a creative AI agent called **Becma** that answers weird complaints about the Normal Objects universe (think Stranger Things, but stranger).

The agent uses **LangChain** — a framework for building AI apps — to pick and use tools freely, in whatever order makes sense for each complaint.

---

## What does it do?

You give it a complaint like *"Why do demogorgons sometimes eat people and sometimes don't?"* and Becma:
1. Decides which tools to use
2. Calls them in whatever order feels right
3. Combines the results into a creative, entertaining answer

---

## Files

| File | What it is |
|---|---|
| `normalobjects_langchain.py` | The main Python script |
| `normalobjects_langchain.ipynb` | Same thing as a Jupyter notebook (easier to read) |
| `lab_summary.md` | Short write-up comparing this approach to LangGraph |
| `.env` | Your secret API key goes here (never shared) |
| `.gitignore` | Tells Git to ignore `.env` and temp files |

---

## How to run it

**Step 1 — Install the packages**
```bash
pip install langchain langchain-openai python-dotenv
```

**Step 2 — Add your OpenAI key to `.env`**
```
OPENAI_API_KEY=sk-your-key-here
```

**Step 3 — Run the script**
```bash
python normalobjects_langchain.py
```

Or open the notebook:
```bash
jupyter notebook normalobjects_langchain.ipynb
```

---

## The 4 Tools Becma can use

| Tool | What it does |
|---|---|
| `consult_demogorgon` | Gets a chaotic, funny perspective from the Demogorgon |
| `check_hawkins_records` | Looks up historical records from Hawkins |
| `cast_interdimensional_spell` | Suggests a creative magical fix |
| `gather_party_wisdom` | Asks Mike, Dustin, Lucas & Will for advice |

The agent picks which tools to use — you don't tell it. That's the whole point.

---

## Tech notes (for the curious)

- Uses `langchain.agents.create_agent` — the current way to build tool-using agents in LangChain 1.2+
- The older `AgentExecutor` approach was removed; this is its replacement
- The agent has no fixed script — it reasons about which tools to call on its own
