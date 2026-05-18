# Project 3 — Hades: Supplier Due Diligence Agent
## What Was Built

> For the lab brief checklist mapped to every requirement → see `LAB_CHECKLIST.md`

---

## TLDR

**Hades** is an autonomous supplier due diligence agent, deployed in production on Railway.

POST a company name, category, and country. Within 60–120 seconds Hades returns a complete risk report: sanctions status, company registry check, 90-day news sentiment, LkSG/CSDDD compliance signals, ESG & labour risk, and live Hermes market intelligence — synthesised by Claude Sonnet 4.6 into a weighted risk score (1–10) with a clear recommendation: **Approve / Conditional Approval / Block**.

It is not a prototype. It is deployed, integrated into SpendLens (spend analytics platform), queryable from Icarus (Telegram-based personal AI OS), and writes to a shared Redis database that Hermes (market intelligence agent) reads for ongoing monitoring.

### Four-Agent Stack

```
ICARUS (Telegram bot · Claude Sonnet 4.6 · icarusai.de)
  ├── hades_supplier_lookup  →  SpendLens + Hades in parallel
  ├── hades_report           →  GET /audit/{company}/latest
  ├── hades_audit            →  GET /audit/{company}
  └── hades_export           →  GET /audit/export/csv → CSV as Telegram attachment

SPENDLENS (spend analytics · React SPA + FastAPI)
  ├── GET /api/suppliers/lookup/{name}   ← fuzzy match against vendor DB
  └── POST /api/hades/investigate        ← triggers DD from SpendLens UI

HADES (this project · FastAPI + LangGraph)
  ├── POST /investigate                  ← main entry point
  ├── GET  /audit/{company}              ← full investigation history
  ├── GET  /audit/{company}/latest       ← most recent record
  └── GET  /audit/export/csv             ← portfolio CSV export

HERMES (market intelligence · ~590 suppliers · Upstash Redis + Vector)
  ├── hermes:supplier:<slug>  ← Hades reads pre-flight
  ├── hermes:watchlist:<slug> ← Hades writes after DD
  └── hades:audit:<slug>      ← Hades writes persistent audit trail
```

### LangGraph Pipeline

```
POST /investigate
      │
hermes_preflight   ← reads Hermes Redis; if >10 signals, skips NewsAPI
      │
┌─────┴──────────────────────────────────────────────┐
│  parallel fan-out (6 nodes)                        │
│  web_research     sanctions_check  registry_lookup  │
│  news_sentiment   lksg_signals     esg_signals      │
└─────────────────────────┬──────────────────────────┘
                          │
                     synthesis          Claude Sonnet 4.6 — scores 6 dimensions
                          │
                 report_generator       Claude Sonnet 4.6 — structured JSON report
                          │
                 hermes_register        writes supplier to Hermes watchlist
                          │
                  audit_writer          persists record to Redis (2yr TTL, max 50/supplier)
                          │
                         END
```

