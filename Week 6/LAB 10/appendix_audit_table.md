# SpendLens — Path B Retrofit Audit Template
### Appendix to: deck_spendlens_green_audit.md

---

## Artifact
**SpendLens — AI-Powered Procurement Intelligence Platform**  
Repo: `eugnmueller-87/PROCUREMENT`  
Modules audited: `icarus_client.py`, `category_strategy.py`, `supplier_profiler.py`, `category_mapper.py`

---

## Primary User Journey
User uploads a spend CSV → SpendLens normalises and categorises rows → User selects a category and clicks "Generate Strategy" → Platform triggers Icarus (RSS + Grok live search + Claude synthesis) + Category Strategy chain (8 sequential Claude calls: Kraljic, PESTEL, SWOT, Porter's, TCO, Levers, Roadmap, Deck export) → Returns a full 10-slide HTML strategy package in ~45 seconds.

**R (functional unit):** One complete category strategy package delivered per user session.

---

## Lever Table (Path A / Path B crossover)

| Lever | Current assumption (honest guess) | Better alternative to explore |
|---|---|---|
| **Model / size** | All 8 strategy subtasks use Claude Sonnet — same large model for Kraljic (high reasoning) and PESTEL bullet expansion (low reasoning) | Tier calls: keep Sonnet for classification/analysis; downgrade to Haiku for structured-output / bullet-fill tasks (est. 40% cost saving per R) |
| **Call pattern (batch, cache, sync)** | 8 sequential LLM calls per strategy run, no caching; Supplier profiler runs 1 call per supplier row (O(n) serial); Icarus re-fetches same RSS feeds on every session trigger | Add SQLite hash-cache for strategy results (TTL 7 days); batch supplier calls 20/request; deduplicate RSS fetch with session-scoped cache |
| **Infra / region / retention** | API calls routed to Anthropic/xAI infrastructure — region unknown; no telemetry; no demand-shaping; Panel runs locally (no idle server cost today, but SaaS deployment changes this) | Request region disclosure from API provider; add `@track_call` telemetry (tokens, latency, cost proxy) before any other change; consider scheduled off-peak batch jobs for non-urgent Icarus runs |

---

## Hotspots (compute / data movement)

| # | Hotspot | Type | Severity |
|---|---|---|---|
| 1 | Category Strategy 8-call chain | Sequential LLM calls, no cache | High — runs every strategy request |
| 2 | Supplier profiler O(n) calls | Serial API calls per row | High — scales with data size |
| 3 | Icarus RSS + Grok + Claude chain | Parallel I/O + LLM synthesis | Medium — redundant on repeat category |
| 4 | Category mapper re-runs on re-upload | Re-classifies identical rows | Medium — common user pattern |
| 5 | No telemetry anywhere | Cannot measure or improve | Critical blocker for all other fixes |

---

## Green Opportunities (prioritised)

1. **[Quick win — 1 day]** Add `@track_call` instrumentation → SQLite telemetry table. Enables every other improvement. No functional change.

2. **[Quick win — 2 days]** Hash-based strategy cache (category + spend hash → cached JSON, TTL 7 days). Estimated 60–80% call reduction for repeat users.

3. **[Medium — 3 days]** Batch supplier profiler (20 suppliers/call via JSON mode). Reduces 200-call jobs to ~12 calls.

4. **[Medium — 3 days]** Model right-sizing: route 4 of 8 strategy subtasks to Haiku after quality eval. Estimated 40% token cost reduction per R.

5. **[Strategic — 2 weeks]** Session-scoped Icarus cache — avoid re-fetching same RSS/Grok data within a single user session or 24h window.

6. **[Strategic — post-SaaS]** Region-aware deployment: route inference to low-carbon region when Anthropic/xAI exposes grid-aware endpoints.

---

## What I Would Measure to Prove Improvement

| Metric | Tool | Baseline target |
|---|---|---|
| Tokens per R (input + output) | `@track_call` → SQLite | Establish week 1; compare week 3 |
| API calls per R | Counter in telemetry | <5 calls/R (from ~8+ today) |
| Cache hit rate | Hit/miss flag in telemetry | >40% within 2 weeks |
| Latency per R (ms) | Start/end timestamps | <30s P95 |
| Cost per R ($) | tokens × published pricing | -30% within 4 weeks |

---

## Risks / Tradeoffs

| Risk | Mitigation |
|---|---|
| Cache staleness — market conditions change, cached strategy becomes outdated | TTL + manual "Refresh Strategy" button; warn user when cache is >3 days old |
| Haiku quality regression on high-stakes outputs | 5-sample quality eval before shipping; never blind-downgrade; keep Sonnet on Kraljic + Negotiation Levers |
| Batching changes prompt structure — may affect output format | Test JSON mode output schema validation before rolling out |
| Region transparency — Anthropic/xAI may not disclose grid intensity | Cannot publish SCI score until this is resolved; be explicit about this gap |
| Instrumentation overhead — logging adds latency | Async write to SQLite; confirmed negligible for <1ms writes |

---

## GSF Pillar Coverage

| Pillar | Solutions addressing it |
|---|---|
| Carbon | Region disclosure (Solution strategic), SCI framing on Slide 10 |
| Energy | Semantic cache (S1), Model right-sizing (S2), Batched profiler (S3), Icarus session cache (S5) |
| Hardware | Batched profiler reduces O(n) calls (S3), Demand shaping / off-peak scheduling (S6) |
| Measurement | Instrumentation layer (S4) — required baseline for all other pillars |

---

*Appendix to: deck_spendlens_green_audit.md*  
*Lab: Ironhack Week 6 LAB 10 — Green Software & Sustainable AI*
