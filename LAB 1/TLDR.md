# TL;DR — LAB 1 (Week 4) | Bloyce's Protocol — Strict Complaint Processor

## What is this?

A rule-based AI complaint processor built with **LangGraph** — complaints about the Downside Up universe must pass through a fixed, auditable 5-step workflow before they can be closed.

---

## The idea in one sentence

> A complaint enters → gets categorized → validated → investigated → resolved → closed, and **cannot skip any step**.

---

## Key concepts (plain English)

| Term | What it means here |
|---|---|
| **LangGraph** | A library that lets you define an AI workflow as a flowchart — nodes + edges |
| **Node** | One step in the workflow (intake, validate, investigate, resolve, close) |
| **Edge** | The connection between steps — defines what happens next |
| **State** | A dictionary that travels through every node and stores all data |
| **Conditional edge** | An edge that branches depending on the state (e.g. valid → investigate, invalid → reject) |
| **LLM** | The AI brain (GPT-4o-mini) used inside each node to make decisions |

---

## How the workflow runs

```
complaint submitted
        ↓
[INTAKE] → categorize into: portal | monster | psychic | environmental | other
        ↓
[VALIDATE] → does it meet category-specific rules?
        ↓              ↓
    VALID           INVALID
        ↓              ↓
[INVESTIGATE]     [REJECT] → explain why → END
        ↓
[RESOLVE] → propose fix + effectiveness rating (high/medium/low)
        ↓
[CLOSE] → confirm, check satisfaction, log timestamp
        ↓
      END
```

---

## The 5 complaint categories

| Category | What qualifies |
|---|---|
| **portal** | Specific location or timing anomaly |
| **monster** | Creature behavior or interaction details |
| **psychic** | Named ability limitation or malfunction |
| **environmental** | Electricity, weather, or observable phenomenon |
| **other** | Anything else → auto-escalated (rejected) |

---

## LangGraph vs LangChain — which is which?

| | LangChain (Lab 1, Week 3) | LangGraph (this lab) |
|---|---|---|
| Workflow shape | Agent decides freely | You define every edge in advance |
| Step order | Emergent (LLM chooses) | Fixed and enforced |
| Good for | Creative, open-ended tasks | Auditable, compliance-level workflows |
| Can skip steps? | Yes | No — graph prevents it |

---

## Files

| File | Purpose |
|---|---|
| `normalobjects_langgraph.py` | Complete LangGraph implementation |
| `lab_summary.md` | Short written comparison (required by lab) |
| `TLDR.md` | This file |
| `README.md` | Setup and run instructions |
| `.env` | Your OpenAI API key (not committed) |
