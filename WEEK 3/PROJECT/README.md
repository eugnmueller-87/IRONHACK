# Hermes + Icarus — AI Market Intelligence System

**Ironhack Week 3 Project Submission**

---

## TL;DR

Hermes watches ~590 tech and AI companies 24/7 — RSS feeds, SEC filings, job boards, earnings calls. Claude Haiku classifies every signal. Claude Sonnet groups them into macro themes. Everything is stored in Redis and a vector index. Icarus (personal Telegram bot) queries Hermes on demand in natural language: *"What do we know about TSMC?"*, *"What macro themes are emerging this week?"*, *"Any signals about chip export controls?"*. The 06:00 morning briefing now includes the top market signals automatically.

**Cost:** ~$7–8/month total. **Deployment:** Railway, 24/7. **Status:** Live.

---

## What Was Built

A two-agent system: **Hermes** (external intelligence) and **Icarus** (personal master agent).

```
You (Telegram)
     │
     ▼
 ICARUS AI  ──── HTTP API ──→  HERMES AGENT
 (master bot)                  (sub-agent)
     │                              │
     │                   RSS · EDGAR · Tavily
     │                   Jobs · Transcripts
     │                   + 18 industry feeds
     │                              │
     │                   Claude Haiku (classify)
     │                   Claude Sonnet (cluster)
     │                              │
     │                 ┌────────────┴────────────┐
     │                 ▼                         ▼
     │           Upstash Redis           Upstash Vector
     │     (items · profiles · clusters)  (semantic RAG)
     └──────── pulls on demand ──────────────────────────┘
```

---

## Intelligence Capabilities

### 1. Signal Detection
Every crawled item is classified by Claude Haiku into one of 11 signal types with urgency (HIGH / MEDIUM / LOW) and a significance flag:

`SUPPLY_CHAIN · PRICING_CHANGE · REGULATORY · ACQUISITION · EARNINGS · LAYOFFS_HIRING · FUNDING · PRODUCT_RELEASE · PARTNERSHIP · RESEARCH_PAPER · OTHER`

### 2. Company Knowledge Profiles
Every signal permanently updates `hermes:profile:{slug}` in Redis — a living company profile with signal counts, urgency breakdown, top signal types, risk flags, and recent history. Ask: *"What do we know about Cerebras?"* → full profile.

### 3. Macro Theme Clustering
`GET /clusters` sends recent significant signals to Claude Sonnet, which groups them into macro themes with synthesis paragraphs and lists the companies involved. Cached 6h.

Example: *"5 chip suppliers flagged export control risk this week — TSMC, ASML, NVIDIA, KLA, Applied Materials."*

### 4. Semantic RAG Search
Upstash Vector (BAAI/bge-large-en-v1.5, 1024-dim, cosine). Ask *"chip export controls"* → returns signals from TSMC, NVIDIA, Applied Materials without naming them.

### 5. Weekly Digest
Every Sunday 18:00, Claude Sonnet reads the week's significant signals grouped by category and writes a category-by-category market summary with an overall verdict. Stored 30 days. Icarus forwards to Telegram at 18:30 automatically.

### 6. Trend Memory
Weekly cluster snapshots stored in Redis. `GET /trends/delta` compares this week vs last week: NEW / CONTINUING / RESOLVED themes. Procurement-relevant drift detection without an LLM in the comparison path.

### 7. Supplier Watchlist
Companies added via `POST /watchlist/{company}` get RSS-crawled every 2 hours instead of every 6 hours. Higher signal frequency for companies that matter most.

### 8. Profile Enrichment
When a company accumulates 10+ significant signals, Claude Haiku auto-extracts `key_products`, `pricing_notes`, and `risk_summary` into the profile. Also triggerable on demand.

### 9. Content Generation Pipeline
6-step pipeline: Redis signals → knowledge base (brand voice + supplier landscape) → Claude Sonnet draft → Telegram staging → Icarus one-tap approval → LinkedIn publish.

---

## Data Sources

| Source | Frequency | Coverage |
|---|---|---|
| RSS + 18 industry feeds | Every 6h | ~590 companies + industry sources |
| SEC EDGAR (8-K, 10-Q, 10-K) | Daily 07:30 | Tier 1+2 public companies |
| Tavily news search | Weekly Mon | Tier 1+2 (~177 companies) |
| Job postings (Lever/Greenhouse) | Weekly Wed | Tier 1+2 — hiring signals |
| Earnings call transcripts (8-K full text) | Weekly Thu | Tier 1+2 |

---

## Icarus Tools (Natural Language → API)

| What you say | Tool called | What happens |
|---|---|---|
| "Greet Hermes" | `hermes_greet` | Live stats from Hermes |
| "What does Hermes have on TSMC?" | `hermes_query` | Recent signals, fuzzy match |
| "What do we know about Cerebras?" | `hermes_profile` | Accumulated company profile |
| "Give me a market briefing" | `hermes_briefing` | Top significant signals |
| "Any signals about chip export controls?" | `hermes_search` | RAG semantic search |
| "What macro themes are emerging?" | `hermes_trends` | Claude Sonnet cluster synthesis |
| "Tell Hermes to run a crawl" | `hermes_crawl` | Triggers crawler on demand (RSS/EDGAR/Tavily/Jobs/Transcripts) |
| "Show me a signals chart" | `hermes_chart` | QuickChart PNG inline photo |
| "What's the weekly digest?" | `hermes_digest` | Latest Sunday market summary |
| "Watch TSMC closely" | `hermes_watch` | Add company to high-frequency watchlist |
| "What themes are new this week?" | `hermes_delta` | NEW / CONTINUING / RESOLVED trend comparison |
| "Enrich the ASML profile" | `hermes_enrich` | Trigger Haiku profile enrichment on demand |

---

## Why Not Just Use ChatGPT?

| | Generic ChatGPT | This System |
|---|---|---|
| Data freshness | Training cutoff | Live: RSS every 6h, SEC daily, Tavily weekly |
| Company specificity | Generic | 590 tracked companies, per-company signal history |
| Automation | Manual prompt every time | Scheduled crawls → classify → profile → cluster |
| Macro intelligence | Single-query | Cross-company trend detection with Claude Sonnet |
| Cost | ~$0 but hours of manual research | ~$7–8/month, zero manual monitoring |

---

## Tech Stack

| Component | Technology |
|---|---|
| API server | FastAPI + uvicorn |
| Scheduler | APScheduler (cron-style) |
| Signal classification | Claude Haiku (Anthropic) |
| Cluster synthesis | Claude Sonnet (Anthropic) |
| Key-value store | Upstash Redis (REST) |
| Vector search | Upstash Vector (BAAI/bge-large-en-v1.5, 1024-dim) |
| News search | Tavily API |
| SEC filings | EDGAR REST API (public, free) |
| Chart generation | QuickChart.io (free) |
| Deployment | Railway (24/7, auto-deploy) |
| Master agent | Telegram bot (python-telegram-bot) + PWA |

---

## Project Files

| File | Purpose |
|---|---|
| `src/content_pipeline.py` | 6-step LinkedIn post generation pipeline |
| `src/knowledge_base.py` | Brand voice + supplier context loader |
| `src/llm_integration.py` | Anthropic API wrapper (Haiku + Sonnet) |
| `src/prompt_templates.py` | 5 prompt templates |
| `config/vscode_agent.json` | VSCode agent config |
| `knowledge_base/primary/` | Brand voice, background, examples, methodology |
| `knowledge_base/secondary/` | Hermes signal samples, supplier landscape |
| `UNIQUENESS.md` | Hermes vs generic ChatGPT comparison |
| `presentation/index.html` | 5-slide project deck |

---

## Ironhack Requirements

| Requirement | Status |
|---|---|
| Primary knowledge base (4 docs) | ✅ brand_voice · background · linkedin_examples · methodology |
| Secondary knowledge base (2 docs) | ✅ hermes_signals_sample · supplier_landscape |
| LLM API integration | ✅ Haiku (classify/brief) + Sonnet (drafts/clusters) |
| Prompt templates (5) | ✅ LINKEDIN_POST · MARKET_BRIEF · SIGNAL_ANALYSIS · CONTENT_CALENDAR · UNIQUENESS_COMPARISON |
| Content generation pipeline | ✅ 6-step, CLI via `src/main.py` |
| VSCode agent config | ✅ `config/vscode_agent.json` |
| Uniqueness comparison | ✅ `UNIQUENESS.md` |
| Presentation (5 slides) | ✅ `presentation/index.html` |
| GitHub Kanban board | ✅ GitHub Projects |
| Pushed to IRONHACK repo | ✅ This repo |

---

## Live Repos

| Repo | URL |
|---|---|
| Hermes Agent (intelligence layer) | [github.com/eugnmueller-87/hermes-agent](https://github.com/eugnmueller-87/hermes-agent) |
| Icarus AI (master agent) | Private |
