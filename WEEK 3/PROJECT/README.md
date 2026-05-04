# Hermes Agent

Hermes is a market intelligence crawler and a supporting sub-agent of **Icarus AI**, a personal operations system, and a live data source for **SpendLens**, a procurement intelligence platform. While Icarus manages your personal world — calendar, email, tasks, Telegram — Hermes watches the external world: tech suppliers, AI companies, semiconductor markets, SEC filings, and research. He stores everything he finds in a shared Redis instance. Icarus and SpendLens pull from it on demand.

---

## Role in the System

```
┌───────────────────────────────────────────────────────────────────┐
│                          ICARUS AI                                │
│                      (Master Agent)                               │
│                                                                   │
│   Gmail · Calendar · Tasks · Telegram · Personal Data             │
│                           │                                       │
│              asks "what do you have on X?"                        │
│                           │                                       │
│             ┌─────────────▼─────────────┐                         │
│             │       Shared Redis        │                         │
│             │      hermes:* keys        │                         │
│             └──────────┬────────────────┘                         │
└────────────────────────┼──────────────────────────────────────────┘
                         │ also reads via HermesClient
┌────────────────────────▼──────────────────────────────────────────┐
│                        SPENDLENS                                  │
│              (Procurement Intelligence Dashboard)                 │
│                                                                   │
│   Panel UI · Icarus pipeline · SQLite · Risk enrichment           │
│   Hermes signals → spend categories → risk flags                  │
└───────────────────────────────────────────────────────────────────┘
                         │ reads
             ┌───────────▼───────────┐
             │      HERMES AGENT     │
             │      (Sub-Agent)      │
             │                       │
             │  RSS · Tavily · EDGAR │
             │  Claude Haiku         │
             │  ~250 companies       │
             └───────────────────────┘
```

**Icarus is master. Hermes never pushes, never alerts, never accesses personal data.**

Hermes writes exclusively to the `hermes:*` Redis namespace. Icarus and SpendLens read from it. This separation is intentional and permanent.

---

## What Hermes Feeds Into

### Icarus AI
Icarus is the master agent that manages your personal operations. Hermes extends it with external market intelligence. Icarus queries Hermes Redis on demand — when you ask about a company, a category, or the day's top signals. In the planned Phase 2, Telegram commands like `"What does Hermes have on TSMC?"` will return structured answers sourced entirely from Hermes data.

### SpendLens
SpendLens is a procurement intelligence dashboard that tracks spend across categories (Cloud & Compute, Hardware, Professional Services, etc.) and surfaces risks using the Icarus analysis pipeline. Hermes enhances it in two ways:

**1. Signal injection into Icarus pipeline**
Every time SpendLens runs an analysis cycle, it calls `HermesClient.get_procurement_briefing()`, which returns the top procurement-relevant signals from Redis (supply chain disruptions, pricing changes, regulatory actions, earnings surprises). These signals are converted into the Icarus signal format — with spend category, relevance score (1-10), and impact direction — and prepended to the analysis pipeline before Claude processes the data.

**2. Vendor risk enrichment**
SpendLens can call `HermesClient.enrich_vendor_list(vendor_names)` to bulk-check any list of vendors against Hermes data. Each vendor gets a risk level (HIGH / MEDIUM / LOW), a signal count, and a reference to the top signal. This feeds directly into SpendLens risk flags and category scores.

```
SpendLens Icarus pipeline
─────────────────────────
1. Load spend data from CSV/Excel
2. [NEW] Pull Hermes procurement signals via HermesClient
3. Analyse with Claude Haiku + local rules
4. Surface top actions, risks, and category alerts in Panel dashboard
```

**Signal type to spend category mapping:**

| Hermes Signal | SpendLens Category |
|---|---|
| SUPPLY_CHAIN | Hardware & Equipment |
| PRICING_CHANGE | Cloud & Compute |
| EARNINGS | Professional Services |
| REGULATORY | Professional Services |
| ACQUISITION | Cloud & Compute |
| LAYOFFS_HIRING | Recruitment & HR |
| FUNDING | AI/ML APIs & Data |
| PRODUCT_RELEASE | Cloud & Compute |

---

## Responsibilities

### What Hermes Does
- Crawls RSS feeds, Tavily news search, and SEC EDGAR filings for ~250 tracked companies
- Classifies every news item by signal type using Claude Haiku
- Stores structured intelligence in Upstash Redis under the `hermes:*` namespace
- Deduplicates items so nothing is processed twice
- Runs continuously on Railway on an automated schedule
- Provides `HermesClient` — a standalone connector for SpendLens and Icarus

### What Hermes Does NOT Do
- Send Telegram messages (Icarus does that)
- Access personal data (email, calendar, tasks)
- Make decisions or take actions
- Push data anywhere — consumers pull on demand

---

## Supplier Coverage

~250 companies across 17 categories, organised into 3 tiers by priority.

| Category | Examples |
|---|---|
| Semiconductors & Chips | NVIDIA, Intel, AMD, TSMC, Qualcomm |
| Memory & Storage | Samsung, Micron, SK Hynix, Western Digital |
| Networking & Connectivity | Cisco, Arista, Juniper, Palo Alto |
| Cloud & Infrastructure | AWS, Azure, Google Cloud, Oracle |
| Servers & IT Hardware | Dell, HPE, Supermicro, Lenovo |
| Contract Manufacturing | Foxconn, Flex, Jabil, Celestica |
| AI Foundation Labs | OpenAI, Anthropic, Google DeepMind, Meta AI |
| AI Infrastructure & Chips | Cerebras, Groq, SambaNova, Tenstorrent |
| AI Agents & Orchestration | LangChain, Cohere, Mistral |
| AI Coding | GitHub Copilot, Cursor, Tabnine |
| Power & Energy | Eaton, Vertiv, Schneider Electric |
| Cybersecurity | CrowdStrike, SentinelOne, Palo Alto |
| + 6 more categories | ... |

**Tier 1** — highest priority, crawled most frequently
**Tier 2** — important, included in weekly Tavily sweep
**Tier 3** — broader coverage, included in full sweeps

---

## Signal Detection

Every item is classified by Claude Haiku into one of 11 signal types:

| Signal | Emoji | Triggers On |
|---|---|---|
| FUNDING | 💰 | Investment rounds, capital raises |
| ACQUISITION | 🤝 | M&A activity, buyouts |
| PRODUCT_RELEASE | 🆕 | New models, hardware, software |
| PRICING_CHANGE | 💲 | API pricing, contract changes |
| SUPPLY_CHAIN | ⚠️ | Disruptions, shortages, delays |
| EARNINGS | 📊 | Financial results, guidance |
| PARTNERSHIP | 🔗 | New partnerships, integrations |
| REGULATORY | ⚖️ | Compliance actions, legal |
| LAYOFFS_HIRING | 👥 | Major headcount changes |
| RESEARCH_PAPER | 🔬 | arXiv, breakthrough research |
| OTHER | 📰 | Everything else |

Each item is also rated **HIGH / MEDIUM / LOW** urgency and flagged `is_significant` if it warrants attention.

---

## Crawl Schedule

| Crawler | Frequency | Coverage | Cost |
|---|---|---|---|
| RSS | Every 6 hours | All companies with RSS feeds | Free |
| EDGAR | Daily 07:30 | US-listed Tier 1+2 companies | Free |
| Tavily | Weekly (Monday 09:00) | Tier 1+2 (~177 companies) | Free tier |

Tavily is intentionally capped at weekly to stay within the free tier (~700 searches/month). ~300 searches/month are reserved for on-demand Icarus queries.

---

## Redis Key Schema

```
hermes:seen:{md5_hash}       Dedup flag — TTL 30 days
hermes:item:{md5_hash}       Full item JSON — TTL 7 days
hermes:supplier:{slug}       List of item IDs per supplier — max 50
```

### Item Schema
```json
{
  "id": "md5 hash of URL",
  "supplier": "NVIDIA",
  "title": "NVIDIA announces new H200 cluster",
  "url": "https://...",
  "summary": "...",
  "published": "2026-05-04T10:00:00Z",
  "source": "rss | tavily | edgar",
  "signal_type": "PRODUCT_RELEASE",
  "is_significant": true,
  "significance_reason": "Major new hardware launch affecting AI infrastructure supply.",
  "urgency": "HIGH",
  "emoji": "🆕"
}
```

---

## Miro Agent

Hermes includes a Miro Agent module (`miro/`) that turns Redis data into visual Miro boards via the Miro REST API.

**Two board types:**

- **Signal Board** — significant items grouped by signal type into frames, sticky notes colour-coded by urgency (red = HIGH, yellow = MEDIUM, green = LOW)
- **Landscape Board** — all suppliers as cards grouped by category, tier-coloured (red = T1, orange = T2, grey = T3)

Boards are created server-side and return a shareable URL. Phase 4 will wire this to Icarus Telegram so you can trigger a board from chat.

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.14 |
| Scheduler | APScheduler |
| News search | Tavily API |
| RSS parsing | feedparser |
| SEC filings | EDGAR REST API (public) |
| Signal detection | Claude Haiku (Anthropic) |
| Storage | Upstash Redis (REST) |
| Deployment | Railway |
| Visual boards | Miro REST API v2 |
| SpendLens connector | HermesClient (difflib fuzzy match) |

---

## Environment Variables

```
ANTHROPIC_API_KEY        Claude Haiku for signal detection
TAVILY_API_KEY           News search
UPSTASH_REDIS_REST_URL   Shared Redis instance (same as Icarus + SpendLens)
UPSTASH_REDIS_REST_TOKEN Shared Redis instance (same as Icarus + SpendLens)
MIRO_ACCESS_TOKEN        Miro REST API (optional — only for board generation)
```

No Telegram variables. Hermes does not send messages.

---

## Project Structure

```
hermes-agent/
├── main.py                         Entry point + APScheduler
├── railway.toml                    Railway deployment config
├── requirements.txt
├── .env.example
├── config/
│   └── suppliers.py                ~250 companies across 17 categories
├── crawlers/
│   ├── rss_crawler.py              RSS feeds — every 6h
│   ├── tavily_crawler.py           Tavily news search — weekly
│   └── edgar_crawler.py            SEC EDGAR filings — daily
├── processors/
│   └── signal_detector.py          Claude Haiku signal classification
├── storage/
│   └── redis_store.py              Upstash Redis interface
├── integrations/
│   └── hermes_client.py            Standalone connector (SpendLens / Icarus)
├── miro/
│   ├── client.py                   Miro REST API wrapper
│   └── boards.py                   Signal board + landscape board builders
├── tests/
├── logs/
├── audit_logs/
└── hermes_explorer.ipynb           Interactive dev notebook (11 sections)
```

---

## Part of the Icarus System

| Agent | Role | Status |
|---|---|---|
| **Icarus** | Master agent — personal operations, Telegram, decisions | Live |
| **Hermes** | Sub-agent — external market intelligence, read-only data source | Live on Railway |
| **SpendLens** | Procurement dashboard — consumes Hermes signals via HermesClient | Integrated |
| **Miro Agent** | Visual boards from Hermes data — signal boards + landscape maps | Built, Telegram wiring pending |
