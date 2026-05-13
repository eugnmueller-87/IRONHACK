# TL;DR — LAB 2 NormalObjects Complaint Handler

## What is this?

An AI agent that answers silly complaints about a fictional universe, using LangChain tools.

---

## The idea in one sentence

> Give the AI a complaint → it picks the right tools → combines answers → gives a fun response.

---

## Key concepts (plain English)

| Term | What it means here |
|---|---|
| **Agent** | An AI that decides *what to do next* by itself, instead of following fixed steps |
| **Tool** | A function the agent can call — like looking up records or asking a character |
| **LangChain** | The Python library that connects the AI to the tools |
| **LLM** | The actual AI brain (GPT-4o-mini in this case) |
| **System prompt** | Instructions that tell the AI who it is and how to behave |

---

## How the agent works (step by step)

```
You send a complaint
       ↓
Agent reads it and thinks: "which tools should I use?"
       ↓
Agent calls Tool 1 → gets an answer
       ↓
Agent calls Tool 2 → gets another answer
       ↓
Agent combines both answers into one response
       ↓
You get a creative, entertaining reply
```

---

## The 4 tools

- **consult_demogorgon** → random chaotic response from the monster
- **check_hawkins_records** → keyword lookup in a fake database
- **cast_interdimensional_spell** → picks random creative "spells" as solutions
- **gather_party_wisdom** → fake quotes from the Stranger Things kids

---

## Why freeform (LangChain) and not structured (LangGraph)?

| | LangChain (this lab) | LangGraph (next lab) |
|---|---|---|
| Tool order | Agent decides freely | You define it in advance |
| Good for | Creative, open-ended tasks | Strict workflows, step-by-step |
| Predictable? | Not really | Yes |
| Fun? | Very | Also yes, different kind |

---

## Files to look at

1. Start with **`normalobjects_langchain.ipynb`** — the notebook explains everything step by step
2. Then read **`lab_summary.md`** — the short write-up for submission
