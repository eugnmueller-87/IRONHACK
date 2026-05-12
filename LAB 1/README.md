# NormalObjects — Bloyce's Protocol (LangGraph)

Strict complaint processor for the Downside Up universe.  
Every complaint must pass through a fixed 5-step workflow: **intake → validate → investigate → resolve → close**.

---

## Files

| File | Description |
|---|---|
| `normalobjects_langgraph.ipynb` | Jupyter notebook — step-by-step walkthrough (start here) |
| `normalobjects_langgraph.py` | Plain Python script version |
| `lab_summary.md` | Required short comparison paragraph |
| `TLDR.md` | Plain-English overview of the project |
| `.env` | Your OpenAI API key (not committed to git) |

---

## Setup

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install langchain langchain-openai langgraph python-dotenv

# 3. Add your API key
# Create a .env file in this folder:
# OPENAI_API_KEY=sk-...
```

---

## Run

```bash
# Jupyter notebook (recommended)
jupyter notebook normalobjects_langgraph.ipynb

# Plain Python script
python normalobjects_langgraph.py
```

---

## Workflow diagram

```
[INTAKE] → categorize complaint
    ↓
[VALIDATE] → check against category rules
    ↓              ↓
[INVESTIGATE]   [REJECT] → END
    ↓
[RESOLVE] → fix + effectiveness rating
    ↓
[CLOSE] → confirm + timestamp
    ↓
  END
```
