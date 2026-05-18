# Project 3 — Supplier Due Diligence Agent
## Roadmap & Build Plan

> **What it is:** A standalone autonomous agent that researches any company and generates a structured Supplier Due Diligence Report — sanctions, news sentiment, company registry, LkSG/CSDDD compliance signals, and Hermes market intelligence. Exposes a clean `POST /investigate` HTTP API consumed by SpendLens and Hermes.
>
> **Where it fits:** Bridges the gap between LAB4 (process agent for existing approved suppliers) and SpendLens (analytics for known spend). Neither handles onboarding a brand new unknown supplier. This does — and hands the supplier off to Hermes for permanent ongoing monitoring.
>
> **Legal context:** The German Supply Chain Due Diligence Act (LkSG, in force Jan 2023) and EU CSDDD (transposition deadline 2026) require companies to actively identify and mitigate human rights and environmental risks in their supply chains. This agent provides the evidence layer for that obligation.
>
> **Why standalone:** Clean `POST /investigate` API → any consumer (SpendLens, Hermes, n8n, future UI) can call it. Debug one thing at a time. Own repo = own portfolio entry. Deploys independently on Railway alongside Hermes.

---

## System Architecture

```
                    ┌─────────────────────────────────────┐
                    │      DD Agent  (standalone)          │
                    │      FastAPI + LangGraph             │
                    │                                      │
  POST /investigate │  ┌── Hermes Check (pre-flight) ──┐  │
  {company,         │  │  HermesClient.get_vendor_intel │  │
   category,        │  │  Already tracked? Pull signals │  │
   country}    ───► │  │  Not tracked? Full research    │  │
                    │  └────────────────┬───────────────┘  │
                    │                   │                   │
                    │  ┌────────────────▼──────────────┐   │
                    │  │    Parallel Research Nodes     │   │
                    │  │  (skip/reduce if Hermes hit)   │   │
                    │  │                                │   │
                    │  │  [Web Research]  Serper.dev    │   │
                    │  │  [News]          NewsAPI DE/EN │   │
                    │  │  [Sanctions]     OpenSanctions │   │
                    │  │  [Registry]      OpenCorporates│   │
                    │  │                + Handelsreg.   │   │
                    │  │  [LkSG/CSDDD]   BAFA, NCP,    │   │
                    │  │                 NGO reports    │   │
                    │  │  [ESG/Labour]   ILO, TI,       │   │
                    │  │                 EcoVadis       │   │
                    │  └────────────────┬───────────────┘   │
                    │                   │                   │
                    │         [Synthesis Node]              │
                    │         Claude — 6 risk dimensions    │
                    │         weighted composite score      │
                    │                   │                   │
                    │         [Report Generator]            │
                    │         Structured DD Report JSON     │
                    │         with LkSG compliance section  │
                    │                   │                   │
                    │  ┌────────────────▼───────────────┐  │
                    │  │       Post-Report Actions       │  │
                    │  │  register_vendor() → Hermes     │  │
                    │  │  watchlist (if new supplier)    │  │
                    │  └─────────────────────────────────┘  │
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │ DD Report JSON
                              ┌─────────┴──────────┐
                              ▼                     ▼
                       SpendLens                 Hermes
                  Compliance Scorecard       Upstash Redis
                  new vendor entry           permanent crawl
                  + due_diligence_reports    coverage starts
```

---

## Hermes Integration — Read First, Write After

This is the key design decision that turns a one-shot research tool into a continuous monitoring loop.

### Pre-flight: Read from Hermes
Before running any external API calls, the agent checks Hermes:

```python
intel = hermes_client.get_vendor_intel(company_name)

if intel["tracked_by_hermes"]:
    # Hermes already has signal history — use it
    # Skip or reduce: NewsAPI calls (Hermes RSS already covered this)
    # Skip or reduce: Tavily/web search (Hermes already crawled)
    # Always run: OpenSanctions, OpenCorporates, LkSG-specific queries
    state["hermes_signals"] = intel["top_signals"]
    state["hermes_risk_flags"] = intel["risk_flags"]
else:
    # Unknown supplier — run all 6 external nodes in full
    state["hermes_signals"] = []
```

**Three scenarios this handles:**

| Scenario | What happens |
|---|---|
| **New supplier, Hermes blind** | Full 6-node research → synthesize → register in Hermes → permanent monitoring starts |
| **Known supplier, Hermes has data** | Pull 6-month signal history → reduce redundant API calls → enrich report with ongoing intelligence |
| **Re-check existing supplier** | Pull Hermes delta since last DD run → generate "what changed?" report without full re-research |

### Post-report: Write to Hermes
After report generation, always call `register_vendor()`:
- If new → Hermes adds to watchlist, crawlers start covering from next cycle
- If already tracked → no-op (safe, idempotent)

---

## Phase 1 — Standalone Scaffold & API Setup
**Goal:** New repo, FastAPI server running, all APIs connected, Hermes client wired.

| Task | Detail |
|---|---|
| New repo | `supplier-dd-agent` — own GitHub repo, own Railway deployment |
| Project scaffold | `api/`, `agent/`, `integrations/`, `tests/`, `demo/`, `.env`, `requirements.txt` |
| FastAPI server | `POST /investigate` endpoint, `GET /health`, `GET /report/{company}` |
| API key setup | Serper.dev, NewsAPI, OpenSanctions (free), OpenCorporates (free tier) |
| Hermes client | Copy `hermes_client.py` from SpendLens — same Upstash Redis credentials |
| Test each API | One script per API — confirm data shape and rate limits |
| DDState schema | `company_name`, `category`, `country`, `hermes_intel`, `web_results`, `news_results`, `sanctions_result`, `registry_result`, `lksg_signals`, `esg_signals`, `risk_scores`, `report`, `is_recheck` |
| LangGraph skeleton | Pre-flight node + 6 parallel nodes + synthesis + report + post-actions — wired, no logic |
| Smoke test | `POST /investigate` with `{"company": "Siemens AG", "category": "Hardware & Equipment", "country": "DE"}` — confirm JSON response |

---

## Phase 2 — Hermes Pre-flight & Research Nodes
**Goal:** Each node returns clean structured data. Hermes pre-flight gates which nodes run at full depth.

### Hermes Pre-flight Node
```python
# nodes/hermes_preflight.py
def hermes_preflight(state: DDState) -> DDState:
    intel = hermes_client.get_vendor_intel(state["company_name"])
    state["hermes_intel"] = intel
    state["hermes_tracked"] = intel["tracked_by_hermes"]
    # Flag which external nodes can run reduced depth
    state["skip_news"] = intel["tracked_by_hermes"] and intel["signal_count"] > 10
    return state
```

### Research Nodes

| Node | File | API | What it returns | Reduced if Hermes hit? |
|---|---|---|---|---|
| **Web Research** | `web_research.py` | Serper.dev | EN + DE queries, top 5 results per query | Reduce to 3 results |
| **News Sentiment** | `news_sentiment.py` | NewsAPI | Last 90 days, EN + DE, negative keyword flagging | Skip if Hermes has >10 signals |
| **Sanctions & Watchlists** | `sanctions_check.py` | OpenSanctions | OFAC, EU, UN, UK, EU Debarment — always runs full | Never reduced |
| **Company Registry** | `registry_lookup.py` | OpenCorporates + Handelsregister (DE via Serper) | Legal name, HRB, status, directors, address | Never reduced |
| **LkSG / CSDDD Signals** | `lksg_signals.py` | Serper targeted queries | BAFA actions, NCP complaints, NGO reports | Never reduced |
| **ESG & Labour** | `esg_signals.py` | Serper + NewsAPI | ILO violations, TI flags, forced/child labour | Reduce if Hermes has ESG signals |

**Parallel execution:** All 6 nodes run concurrently — target < 15s total.

---

## Phase 3 — Synthesis & Report Generation
**Goal:** Claude scores 6 risk dimensions and generates a structured report that explicitly cites Hermes signals as "ongoing monitoring intelligence."

### Risk Scoring (synthesis node)
Claude receives all research outputs and scores independently:

| Dimension | Weight | What drives it |
|---|---|---|
| Sanctions Risk | 25% | OpenSanctions match, EU debarment |
| Registry Risk | 15% | Company status, dissolved subsidiaries, jurisdiction flags |
| News Sentiment | 15% | Negative article count, severity, recency |
| LkSG / CSDDD Risk | 20% | BAFA actions, NCP complaints, NGO investigations |
| ESG & Labour Risk | 15% | ILO violations, environmental fines, child/forced labour |
| Hermes Intelligence | 10% | Ongoing HIGH/MEDIUM urgency signals from crawlers |

Output: `risk_score` (1–10 per dimension), `overall_risk_score` (weighted avg), `risk_level` (Low / Medium / High / Critical), `risk_factors` list, `positive_signals` list.

### Report Structure (report generator node)
```
1. Executive Summary
   - Recommendation: Approve / Conditional Approval / Block
   - Overall Risk Score + Risk Level
   - Top 3 risk factors
   - Hermes monitoring status: "Tracked since X" or "Now registered for monitoring"

2. Company Overview
   - Legal name, HRB, jurisdiction, incorporation date, status, directors

3. Sanctions & Watchlist Status
   - OpenSanctions result, datasets checked, matched entities (if any)

4. News Sentiment (last 90 days)
   - Article count, negative flag count, top concerning headlines

5. LkSG / CSDDD Compliance Assessment
   - BAFA enforcement actions (yes/no + detail)
   - NCP complaints (yes/no + detail)
   - NGO reports (yes/no + detail)
   - Conclusion: Compliant / Needs Monitoring / Red Flag

6. ESG & Labour Signals
   - ILO violations, environmental fines, child/forced labour findings

7. Hermes Ongoing Intelligence
   - Signal history summary (if tracked)
   - Recent HIGH/MEDIUM urgency signals
   - "First monitored: [date]" or "Added to monitoring: [today]"

8. Risk Score Breakdown (per dimension with rationale)

9. Required Next Steps (only if Conditional or Block)
```

Output: clean JSON via Claude tool_use. Never free text.

---

## Phase 4 — Post-Report Actions & Integrations
**Goal:** Every DD run feeds both Hermes and SpendLens automatically.

### Hermes Registration (always runs after report)
```python
# nodes/hermes_register.py
def hermes_register(state: DDState) -> DDState:
    is_new = hermes_client.register_vendor(
        vendor_name=state["company_name"],
        category=state["category"],
        country=state["country"],
        source="dd_agent",
    )
    state["hermes_registered"] = is_new  # True = newly added, False = already tracked
    return state
```

### SpendLens Connector
```python
# integrations/spendlens_connector.py
# Called by SpendLens "Run Due Diligence" button via HTTP
# Writes to spendlens.db:
#   vendors table → new vendor with compliance_score, tier, status pre-filled from DD report
#   due_diligence_reports table → full DD report JSON + timestamp
#   audit_log → DD run record
```

**Field mapping: DD Report → SpendLens vendor schema**

| DD Report field | SpendLens field |
|---|---|
| `overall_risk_score` (inverted) | `compliance_score` (0–100) |
| `risk_level` | `tier` (Low=A, Medium=B, High/Critical=C) |
| `recommendation` | `status` (Approve=preferred, Conditional=conditional, Block=blocked) |
| `registry.company_status` | `active` flag |
| `category` | SpendLens taxonomy category |
| `registry.country` | `region` |

### Re-check Flow
```
GET /investigate/{company}?mode=recheck
  → pull Hermes signals since last_dd_run date
  → run only: OpenSanctions (always fresh), LkSG queries (always fresh)
  → skip: registry (unchanged), ESG (use Hermes delta)
  → generate delta report: "Since last check on [date], X new signals found"
```

---

## Phase 5 — Demo & Portfolio Polish
**Goal:** Three clean demo scenarios, architecture diagram, strong README, Railway deployment.

| Task | Detail |
|---|---|
| Demo scenario 1 | Clean DACH supplier not in Hermes → full research → registered → Low risk report |
| Demo scenario 2 | Supplier with known LkSG exposure (real case) → Medium/High risk → Conditional + next steps |
| Demo scenario 3 | Sanctioned entity → Critical risk → Block recommendation, EU dataset match shown |
| Demo scenario 4 | Re-check a supplier from scenario 1 → Hermes now has signals → delta report |
| Architecture diagram | Clean PNG showing full flow: FastAPI → LangGraph → APIs → Hermes → SpendLens |
| README | Problem, LkSG/CSDDD legal context, architecture, APIs, how to run, demo output |
| Railway deployment | `railway.toml`, deploy alongside Hermes, `HERMES_API_KEY` shared secret |
| Code cleanup | No debug prints, docstrings on key functions, consistent error handling |
| Push to GitHub | New public repo `supplier-dd-agent` |

---

## API & Source Reference

### Core APIs
| API | Free Tier | Auth | Used for |
|---|---|---|---|
| [Serper.dev](https://serper.dev/) | 2,500 free searches | API key (header) | Web research, LkSG signals, ESG, Handelsregister fallback |
| [NewsAPI.org](https://newsapi.org/) | 100 req/day (dev) | API key (param) | News sentiment EN + DE |
| [OpenSanctions](https://www.opensanctions.org/api/) | Free | Optional key | OFAC, EU, UN, UK, EU Debarment — 100+ datasets |
| [OpenCorporates](https://api.opencorporates.com/) | Free tier | API token | Company registry, legal status |

### Hermes Integration
| Component | How used |
|---|---|
| `HermesClient.get_vendor_intel()` | Pre-flight — pull existing signals before external API calls |
| `HermesClient.get_risk_flags()` | Enrich synthesis — HIGH/MEDIUM urgency signals as risk evidence |
| `HermesClient.register_vendor()` | Post-report — add new supplier to Hermes watchlist |
| Upstash Redis | Same credentials as SpendLens (`UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`) |
| Upstash Vector | Semantic search — `GET /search?q={company} supply chain risk` |

### German & EU Sources (via Serper queries)
| Source | Covers |
|---|---|
| BAFA (bafa.de) | LkSG enforcement actions |
| OECD NCP / BMWK | NCP complaints against German companies |
| Handelsregister (handelsregister.de) | Official DE company registry, HRB number |
| Transparency International | Corruption perception, sector reports |
| ILO / ITUC | Forced labour, child labour, freedom of association |
| Germanwatch / ECCHR | Civil society LkSG monitoring |

### LkSG / CSDDD Legal Context
| Law | Scope | Key obligations |
|---|---|---|
| **LkSG** (DE, Jan 2023) | Companies >1,000 employees in DE | Risk analysis, preventive measures, complaints mechanism, BAFA annual report |
| **CSDDD** (EU, 2026) | EU companies >500 employees + €150M turnover | Full value chain, environmental due diligence, civil liability |
| **EU Forced Labour Regulation** | All companies selling in EU | Products made with forced labour banned from EU market |

---

## Tech Stack

| Component | Technology |
|---|---|
| HTTP server | FastAPI (Python) |
| Agent framework | LangGraph |
| LLM | Claude API — claude-sonnet-4-6 |
| Web research + LkSG/ESG | Serper.dev |
| News (EN + DE) | NewsAPI.org |
| Sanctions & watchlists | OpenSanctions |
| Company registry | OpenCorporates + Handelsregister (DE via Serper) |
| Hermes integration | `HermesClient` → Upstash Redis + Vector |
| Storage | SQLite (SpendLens DB, via connector) |
| Deployment | Railway (alongside Hermes) |

---

## Success Criteria

| Criterion | Target |
|---|---|
| All APIs returning data | 100% |
| Hermes pre-flight correctly detects known suppliers | Validated on 5 suppliers already in Hermes |
| New supplier registered in Hermes after DD run | 100% |
| Correct sanctions flag on known sanctioned entities | 100% |
| LkSG section populated for companies with known BAFA exposure | Validated on real cases |
| Report generated end-to-end | < 30 seconds (new supplier), < 15 seconds (Hermes hit) |
| SpendLens Compliance Scorecard updated | New vendor visible after DD run |
| Re-check returns delta report | Validated on supplier from initial onboarding |
| Demo runs without errors | 4 scenarios clean |

---

## File Structure

```
supplier-dd-agent/
├── ROADMAP.md
├── README.md
├── railway.toml                        ← Railway deployment config
├── .env                                ← API keys (gitignored)
├── .gitignore
├── requirements.txt
├── main.py                             ← FastAPI entrypoint
├── api/
│   └── routes.py                       ← POST /investigate, GET /health, GET /report/{company}
├── agent/
│   ├── graph.py                        ← LangGraph definition
│   ├── state.py                        ← DDState TypedDict
│   ├── nodes/
│   │   ├── hermes_preflight.py         ← Read from Hermes before external calls
│   │   ├── web_research.py             ← Serper.dev
│   │   ├── news_sentiment.py           ← NewsAPI EN + DE
│   │   ├── sanctions_check.py          ← OpenSanctions
│   │   ├── registry_lookup.py          ← OpenCorporates + Handelsregister
│   │   ├── lksg_signals.py             ← BAFA, NCP, NGO via Serper
│   │   ├── esg_signals.py              ← ILO, TI, EcoVadis via Serper
│   │   ├── synthesis.py                ← Claude risk scoring (6 dimensions)
│   │   ├── report_generator.py         ← Claude structured DD report
│   │   └── hermes_register.py          ← Write new supplier to Hermes watchlist
│   └── prompts.py                      ← All Claude prompts
├── integrations/
│   ├── hermes_client.py                ← Copied from SpendLens, same Redis credentials
│   └── spendlens_connector.py          ← Writes DD report to spendlens.db
├── tests/
│   ├── test_nodes.py
│   ├── test_hermes_flow.py             ← Test pre-flight + registration
│   └── test_graph.py
└── demo/
    └── run_demo.py                     ← 4-scenario demo script
```
