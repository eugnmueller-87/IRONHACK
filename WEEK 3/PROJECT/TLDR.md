# Hermes Agent — TL;DR

**What it is:** A market intelligence crawler that runs 24/7 on Railway, watches ~250 tech and AI companies, and feeds structured signals to Icarus AI and SpendLens.

**Why it exists:** Icarus handles your personal world — email, calendar, Telegram. Someone had to watch the external world — supplier risks, AI funding, SEC filings, pricing changes. That's Hermes.

**How it works:** Three crawlers pull data continuously. Claude Haiku classifies every item into one of 11 signal types with urgency scoring (HIGH / MEDIUM / LOW). Everything lands in Upstash Redis under the `hermes:*` namespace. Two systems read from it.

---

| | |
|---|---|
| **Coverage** | ~250 companies · 17 categories · 3 tiers |
| **Crawlers** | RSS every 6h · EDGAR daily · Tavily weekly |
| **Signal types** | 11 (FUNDING, SUPPLY_CHAIN, PRICING_CHANGE, EARNINGS, ...) |
| **Storage** | Upstash Redis · 7-day TTL · dedup · `hermes:*` namespace |
| **Deployment** | Railway · 24/7 · auto-deploys on push |
| **Cost** | ~$6/month (Railway hosting only — all APIs on free tiers) |

---

**Who reads it:**

- **Icarus AI** — on demand via Telegram:
  - *"give me a Hermes briefing"* → top signals today
  - *"what does Hermes have on TSMC?"* → company signals
  - *"build a Miro board"* → visual landscape board + URL
  - *"build a signals board"* → visual signal board + URL

- **SpendLens** — automatically on every analysis cycle via `HermesClient`, which injects procurement signals directly into the Icarus analysis pipeline and enriches vendor risk scores.

---

**Status:** Live. All crawlers running. SpendLens integrated. Miro boards working. Icarus Telegram commands live.
