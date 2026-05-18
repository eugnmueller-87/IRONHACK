# Project 3 — Lab Brief Checklist
## Every requirement from the brief mapped to what was built

---

## Project Requirements

---

### ✅ **Implement an agent-based system**

> *Use LangChain, LangGraph, n8n, or another justified agent/workflow approach, and explain why your choice fits the use case*

- **Framework:** LangGraph StateGraph
- **Why LangGraph:** 6 research nodes are fully independent — LangGraph `Send` API runs all in parallel (<120s total). LangChain would chain them sequentially (~6× slower). n8n was considered but Python-native execution gave tighter Redis/Claude integration.
- **9-node pipeline:** `hermes_preflight` → fan-out (6 parallel) → `synthesis` → `report_generator` → `hermes_register` → `audit_writer`
- **State management:** `DDState` TypedDict in `agent/state.py` — single state object flows through all nodes
- **Files:** `agent/graph.py` · `agent/state.py` · `agent/nodes/`

---

### ✅ **Integrate a minimum of two real API tools**

> *MCP tools, direct API integrations, n8n nodes, or custom tools*

**7 real API integrations (minimum required: 2):**

| # | API / Source | Type | Used for |
|---|---|---|---|
| 1 | **Anthropic Claude Sonnet 4.6** | REST API | Risk synthesis + structured report generation |
| 2 | **Serper.dev** | REST API | Web research · LkSG/BAFA queries · ESG queries · registry fallback |
| 3 | **newsapi.ai (Event Registry)** | REST API | News sentiment — last 90 days, EN + DE |
| 4 | **OFAC SDN XML** | Free public XML | US Treasury sanctions list — parsed + cached 24h |
| 5 | **UN SC Consolidated List XML** | Free public XML | UN Security Council sanctions — parsed + cached 24h |
| 6 | **NorthData** | Via Serper | German company registry (HRB, legal status, directors) |
| 7 | **Upstash Redis** | REST API | Hermes pre-flight reads · audit trail writes · watchlist writes |

---

### ✅ **Generate comprehensive reports**

> *Well-structured written reports that synthesize findings in a format appropriate to the use case*

- **Output format:** Structured JSON via Claude tool_use — never free text
- **9-section report structure:**
  1. Executive Summary (recommendation + top 3 risk factors)
  2. Company Overview (HRB, jurisdiction, legal status, directors)
  3. Sanctions & Watchlist Status (OFAC + UN SC results)
  4. News Sentiment (last 90 days, EN + DE)
  5. LkSG/CSDDD Compliance Assessment (BAFA, NCP, NGO signals)
  6. ESG & Labour Signals (ILO, Transparency International, Violation Tracker)
  7. Hermes Ongoing Intelligence (market signal history)
  8. Risk Score Breakdown (per dimension with rationale)
  9. Required Next Steps (only for Conditional / Block)
- **Risk scoring:** weighted composite across 6 dimensions → score 1–10 → Low / Medium / High / Critical

---

### ✅ **Handle errors gracefully**

> *Error handling, retry logic, and validation for tool calls and API interactions*

- Every research node wrapped in `try/except` — single node failure never crashes the pipeline
- `parse_json_response()` helper in `agent/nodes/_utils.py` retries Claude once on malformed JSON output
- `audit_writer` failure silently swallowed — audit failure never breaks the DD response
- `raise_for_status()` on all HTTP proxy calls in SpendLens — Hades error responses propagate as proper HTTP status codes (not swallowed as 200)
- Sanctions XML fetched once at startup, cached 24h in-memory — no per-request re-download
- Redis unavailable at pre-flight → all 6 nodes run full depth, no crash
- DB connection leaks fixed: all SQLite connections moved to `try/finally` blocks

---

### ✅ **Plan the work with Agile methods**

> *User stories, sprint tasks, estimates, dependencies, and definitions of done*

- **File:** `supplier-dd-agent/docs/stories.md`
- **10 user stories** across 4 sprints covering: core pipeline · parallel nodes · sanctions · LkSG · Hermes pre-flight · Hermes registration · audit trail · CSV export · SpendLens integration · Icarus dual-check
- Every story has: acceptance criteria · estimate in days · named dependencies · definition of done with checkboxes
- Sprint summary table: Sprint 1–4, all marked complete
- Velocity notes: documents planning pivots (why OFAC XML over OpenSanctions, why newsapi.ai over NewsAPI.org dev tier, etc.)

---

### ✅ **Document agent instructions and skills**

> *Project specification written for the agent, every AGENTS.md file, all project skills under skills/*

- **AGENTS.md:** `hades/AGENTS.md` at repo root — covers identity, trigger format, all 7 tools with always/conditional flags, full LangGraph pipeline, risk scoring weights, hard guardrails, all API endpoints, env vars, error policy per failure mode
- **skills/ directory:** `Personal-Assistent/bot/skills/hades.py` — 4 Claude tool definitions with name, description, input_schema, and handler

| Tool in skills/ | What it exposes |
|---|---|
| `hades_supplier_lookup` | SpendLens spend data + Hades audit in parallel — one merged answer |
| `hades_report` | Full latest DD report with dimension bar chart |
| `hades_audit` | Full investigation history newest first |
| `hades_export` | CSV file download sent as Telegram document |

---

## Necessary Deliverables

---

### ✅ **GitHub repository — organised, documented code**

- **Repo:** `github.com/eugnmueller-87/hades` (public)
- **README:** problem statement · LkSG/CSDDD legal context · four-agent architecture diagram · full API docs · setup instructions · env vars · 4 demo scenarios
- **requirements.txt:** all dependencies listed
- **Project structure:** `api/` · `agent/nodes/` · `integrations/` · `demo/` · `tests/`
- **Commit history:** ~20 commits, each scoped to one change with a descriptive message, across hades · Icarus · SpendLens · Hermes repos
- **Architecture diagrams:** four-agent ASCII diagram in every repo README; internal LangGraph pipeline diagram in Hades README
- **docs/stories.md:** 10 user stories with estimates, dependencies, definitions of done — `supplier-dd-agent/docs/stories.md`
- **skills/ directory:** `Personal-Assistent/bot/skills/hades.py`
- **AGENTS.md:** `hades/AGENTS.md`

---

### ✅ **Working autonomous agent**

- **Trigger:** `POST /investigate {"company": "...", "category": "...", "country": "DE"}`
- **End-to-end flow:** trigger → 9-node LangGraph pipeline → structured JSON report → Hermes watchlist registration → Redis audit record
- **No human intervention** required after trigger fires
- **Minimum 2 API integrations:** 7 implemented (see list above)
- **Complete workflow:** research → synthesis → report → post-actions (watchlist + audit)
- **Error handling:** per node try/except · JSON retry · status code validation · connection leak fixes
- **Architecture decisions documented:** ROADMAP.md "Why standalone" · "Hermes Integration — Read First Write After" · API source reference with free vs paid breakdown

**Optional advanced components used:**

| Component | Status |
|---|---|
| LangGraph workflow | ✅ Used — 9-node StateGraph with Send API fan-out |
| RAG system | ✅ Used — Hermes pre-flight reads Upstash Vector semantic index |
| Webhook / HTTP trigger | ✅ Used — FastAPI `POST /investigate` |
| Monitoring / audit trail | ✅ Used — Redis-backed audit history, CSV export |

---

### ✅ **Generated report examples (minimum 2–3)**

**4 demo scenarios, runnable via `demo/run_demo.py`:**

| # | Company | Score | Risk | Recommendation | What it demonstrates |
|---|---|---|---|---|---|
| 1 | Schindler Group (CH) | 5.0 | Medium | Conditional Approval | Clean DACH supplier, new to Hermes — full 6-node research, auto-registered to watchlist |
| 2 | H&M Group (SE) | 6.0 | High | Conditional Approval | LkSG/ESG exposure — BAFA/NGO red flags surfaced in compliance section |
| 3 | Huawei Technologies (CN) | 7.0 | High | Block | Geopolitical + sanctions adjacency — Block recommendation triggered |
| 4 | Schindler Group (recheck) | 4.0 | Medium | Conditional Approval | Hermes feedback loop — pre-flight uses 6-month cached signals, faster + cheaper |

Scenario 4 is the key differentiator: it demonstrates the Hermes feedback loop where a previously investigated supplier returns faster because Hermes pre-flight data replaces NewsAPI calls.

---

### ⚠️ **Demo video or live presentation (5–7 minutes)**

- `demo/run_demo.py` runs all 4 scenarios end-to-end from the terminal
- SpendLens UI has a live 10-step pipeline tracker showing real-time progress
- **To do:** record the 5–7 min walkthrough video

---

### ✅ **Documentation**

- **Architecture overview:** four-agent stack diagram in every repo README
- **Workflow diagrams:** internal LangGraph pipeline diagram in Hades README
- **API integration details:** every endpoint documented with request/response examples in Hades README + AGENTS.md
- **Tool descriptions:** all 7 APIs documented with purpose, key type, and usage in AGENTS.md
- **Setup and deployment instructions:** local run (venv + uvicorn) and Railway deployment in Hades README
- **Agile planning artifacts:** `docs/stories.md` with estimates, dependencies, definitions of done
- **Agent-facing specification:** `AGENTS.md` at repo root
- **Skills documentation:** `skills/hades.py` with tool descriptions and input schemas

---

## Evaluation Criteria

---

### ✅ **Requirements Completion (25%)**

| Criterion | Status | Detail |
|---|---|---|
| Agent-based system using justified architecture | ✅ | LangGraph StateGraph — justification in README |
| Minimum 2 real tools/APIs | ✅ | 7 integrated |
| Comprehensive reports generated autonomously | ✅ | 9-section JSON report, 4 demo scenarios |
| Error handling, retry logic, validation | ✅ | Per-node try/except, JSON retry, status checks, connection fixes |
| Agile planning artifacts with estimates + DoD | ✅ | `docs/stories.md` — 10 stories, 4 sprints |

---

### ✅ **Agent Architecture & Implementation (30%)**

| Criterion | Status | Detail |
|---|---|---|
| Well-designed workflow trigger → report | ✅ | `POST /investigate` → 9-node LangGraph → JSON response |
| Framework choices justified | ✅ | LangGraph (parallel), FastAPI (async), Claude tool_use (structured output) |
| Tool calls, context, synthesis integrated coherently | ✅ | All 6 node outputs merge into DDState; synthesis → report_generator → post-actions |
| State, routing, prompts clear and maintainable | ✅ | `DDState` TypedDict · `prompts.py` · one file per node |
| Operates autonomously after trigger | ✅ | Zero human input required after `POST /investigate` |

---

### ✅ **Quality & Execution (25%)**

| Criterion | Status | Detail |
|---|---|---|
| Code organised and maintainable | ✅ | `api/` · `agent/nodes/` · `integrations/` — each node ~80 lines |
| Tool/API integrations reliable, validated, documented | ✅ | Status checks · XML caching · fuzzy name matching · connection leak fixes |
| Reports accurate, useful, appropriate structure | ✅ | 9-section report, real demo scenarios on real companies |
| Proper version control with meaningful commits | ✅ | ~20 descriptive commits across 4 repos |
| Advanced components implemented effectively | ✅ | LangGraph fan-out · Redis audit trail · parallel ThreadPoolExecutor · CSV streaming |

---

### ⚠️ **Documentation & Presentation (20%)**

| Criterion | Status | Detail |
|---|---|---|
| Clear README with setup instructions | ✅ | Full README in Hades repo |
| Architecture diagrams and workflow documentation | ✅ | Four-agent diagram + pipeline diagram in all READMEs |
| User stories, sprint plan, estimates, definitions of done | ✅ | `docs/stories.md` |
| Agent-facing specification and AGENTS.md | ✅ | `hades/AGENTS.md` |
| skills/ directory | ✅ | `Personal-Assistent/bot/skills/hades.py` |
| Effective demonstration of working system | ✅ | `demo/run_demo.py` · SpendLens live pipeline tracker |
| Clear explanation of design decisions | ✅ | ROADMAP.md + README |
| **Demo video (5–7 min)** | ⚠️ | **Still to record** |

---

## One Item Remaining

| Item | What's needed |
|---|---|
| **Demo video** | 5–7 min walkthrough: trigger `POST /investigate` → show pipeline running → show report output → show Hermes registration → show Icarus Telegram query → show SpendLens DD tab |
