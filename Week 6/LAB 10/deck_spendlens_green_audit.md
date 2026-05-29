# SpendLens Carbon Story — Green Software Audit Deck (v2 — Code-Verified)
### Path B — Green Retrofit Audit
**Eugen Mueller | Ironhack AI Engineering Bootcamp | Week 6 LAB 10**

---

## Slide 1 — Hook

**Artifact:** SpendLens — AI-Powered Procurement Intelligence Platform  
**Audience:** CTO / Head of Engineering considering SaaS productisation  
**Audit version:** v2 — updated after reading the actual source code (not assumptions)

**Why green software matters here:**  
SpendLens runs LLM API chains on every user action. The Category Strategy tab triggers 7 sequential Claude calls per session. The Icarus agent runs 20+ parallel RSS fetches plus up to 4 Grok API calls on every deep scan, followed by batched Haiku analysis. The weekly summary and targeted query functions each invoke Sonnet — the largest model in the stack — on demand.

As SpendLens moves from prototype to multi-tenant SaaS, every unoptimised pattern multiplies linearly with users. The original v1 audit was based on code reading assumptions. This v2 audit corrects three of those assumptions by reading the actual code.

> **What changed between v1 and v2:** Model right-sizing (Solution 2) and category mapper caching (hotspot 4) were already implemented. Supplier profiler has no LLM calls. Two new real hotspots were found: Icarus `query_with_claude` re-fetches RSS live on every question, and Sonnet is used where Haiku would suffice.

---

## Slide 2 — One Unit of Value (R)

**R = one complete Category Strategy package delivered per user session**

That package includes:
- Kraljic quadrant classification
- PESTEL analysis
- SWOT analysis
- Porter's Five Forces
- TCO breakdown
- Negotiation levers narrative
- 3-year strategy recommendation

**Why R matters here:**  
R is the billing unit. Every improvement is measured as *change in resource consumption per R* — not per API call, not per token batch. If we reduce calls-per-R, cost and carbon exposure drop proportionally even as user count grows.

**Secondary R worth tracking:**  
- One Icarus deep scan (big mode): 20+ feeds + 4 Grok calls + N batch Haiku calls
- One targeted Icarus query: 1 Sonnet call + live RSS re-fetch

---

## Slide 3 — Assessment Defense: Hotspots (Code-Verified)

**Where compute concentrates — verified by reading the source:**

| Hotspot | Evidence in code | Pattern | Severity |
|---|---|---|---|
| Category Strategy 7-call chain | `generate_all_frameworks()` — 6 steps + recommendation, sequential, no cache | Serial LLM, no cache | HIGH |
| Icarus `query_with_claude` live re-fetch | `fetch_articles()` called inside every query — full RSS re-fetch regardless of recency | No session cache | HIGH |
| Sonnet for query + weekly summary | `query_with_claude` and `weekly_summary` use `claude-sonnet-4-6`; Haiku would suffice for structured extraction | Oversized model | MEDIUM |
| Icarus big-scan: 4 Grok clusters | `_GROK_CLUSTERS` — 4 parallel xAI calls per deep scan, even for narrow category selections | No scope filter | MEDIUM |
| No telemetry anywhere | No `@track_call`, no logging of tokens/latency/cost per R | Zero measurement | CRITICAL |

**What v1 got wrong (corrected):**
- Supplier profiler has **zero LLM calls** — pure rule-based scoring. Not a hotspot.
- Category mapper already has a **vendor_cache.json** — re-uploads cost $0 in API calls. Not a hotspot.
- Icarus analysis already **batches 15 articles/call** with 5 parallel workers. Not a hotspot.
- Category Strategy already uses **Haiku** for all 7 framework calls. Model right-sizing already done.

> *Skeptical stakeholder: "How confident are you in these hotspots?"*  
> High confidence on structure (read the code). No confidence on magnitude (no telemetry). Slide 10 defines the measurement plan.

---

## Slide 4 — Assessment Defense: Assumptions

**Five honest guesses — what we still do not know after reading the code:**

1. **API Region:** Claude API and Grok API calls are routed to Anthropic/xAI infrastructure. Region is not configured in the codebase — it is determined by Anthropic/xAI routing. Grid carbon intensity varies 3–10× between US-East and EU-West.

2. **Token counts per call:** Strategy prompts include full spend data as context. Token count per call not instrumented. Estimated 2,000–5,000 tokens per framework call — but could be 2× higher for categories with many vendors in the spend summary.

3. **Icarus query frequency:** We do not know how often users trigger `query_with_claude` vs. the cached signal feed. If users ask 5+ questions per session, each re-fetching RSS, the live-fetch hotspot is significant.

4. **Grok scan frequency:** Big-scan mode costs ~$0.13/run including Grok. Not known how often users trigger this. If daily per client, Grok spend scales fast.

5. **Multi-tenant concurrency:** Strategy generation is currently synchronous. Under concurrent multi-tenant load, 7 sequential calls per user × N users = N×7 queued Haiku calls. No connection pooling or rate-limit handling visible.

**What we would validate first:** add `@track_call` logging — 1 day of work, zero functional change.

---

## Slide 5 — Pillars Map

**How verified hotspots touch the four GSF pillars:**

```
                    CARBON
                    ├── Unknown inference region — grid intensity unknown
                    └── Cannot publish SCI score without I (grid intensity)

         ENERGY                          HARDWARE
         ├── 7 sequential Haiku calls    ├── No demand-shaping
         │   per strategy R, no cache   ├── Synchronous strategy gen blocks
         ├── Icarus query re-fetches     │   thread under concurrent load  
         │   full RSS on every question  └── No off-peak scheduling for
         └── Sonnet where Haiku              big-mode Icarus scans
             suffices (query + weekly)

                    MEASUREMENT
                    ├── Zero telemetry (tokens, latency, cost/R)
                    ├── No SCI proxy metric defined
                    └── Cannot prove any improvement without a baseline
```

**Priority:** Measurement first → Energy (highest ROI) → Hardware → Carbon (requires infra control).

---

## Slide 6 — Solution 1: Strategy Result Cache

**Problem:** Category Strategy chain runs all 7 Haiku calls even when the underlying spend data and category selection have not changed since the last run for that client.

**Change:**  
Add a hash-based cache keyed on `(client_name + category + spend_data_hash)`.  
Cache the full `{framework: {data, updated_at}}` dict in SQLite with a 7-day TTL.  
On cache hit: `load_strategy()` already exists — extend it with a freshness check. Skip `generate_all_frameworks()` entirely.

```python
# category_strategy.py — add to generate_all_frameworks()
cache_key = hashlib.md5(f"{client_name}:{category}:{spend_hash}".encode()).hexdigest()
cached = load_strategy_if_fresh(client_name, category, ttl_days=7)
if cached and len(cached) == 7:
    return cached  # skip all 7 API calls
```

**Pillar(s):** Energy · Carbon  
**Green Software Pattern:** Static Assets — serve pre-computed results instead of recomputing

**Business outcome:** 60–80% call reduction for returning users. Latency: ~40s → <100ms on cache hit. Direct API cost saving proportional to repeat rate.

**Tradeoff:** Cached strategy goes stale if market conditions shift. Mitigated by 7-day TTL + a "Refresh Strategy" button that bypasses cache.

---

## Slide 7 — Solution 2: Haiku for Icarus Query & Weekly Summary

**Problem:** `query_with_claude` and `weekly_summary` both use `claude-sonnet-4-6`. These functions do structured JSON extraction from a fixed prompt with a defined output schema — a task Haiku handles reliably at ~15× lower token cost.

**Change:**  
Route both functions to `claude-haiku-4-5-20251001`. Keep Sonnet only for open-ended reasoning tasks where quality matters (currently none in the codebase — Haiku already handles all strategy frameworks).

```python
# icarus.py — two lines to change:
# query_with_claude:   model="claude-haiku-4-5-20251001"
# weekly_summary:      model="claude-haiku-4-5-20251001"
```

Add a 5-sample quality eval: compare Haiku vs Sonnet output on 5 real queries before shipping.

**Pillar(s):** Energy · Carbon · Hardware  
**Green Software Pattern:** Optimize AI Model — use the smallest model that meets quality requirements

**Business outcome:** ~15× token cost reduction on every Icarus query and weekly summary. No change to output format or downstream UI code.

**Caveat:** Never a blind downgrade. Run the quality eval first. If Haiku fails on complex multi-document RFP briefs, keep Sonnet for `generate_rfp_brief` only.

---

## Slide 8 — Solution 3: Session Cache for Icarus Live Queries

**Problem:** `query_with_claude` calls `fetch_articles(client_categories)` at the top of every question — re-fetching all 20+ RSS feeds on every user question within the same session, even if the user asks three questions in a row.

**Change:**  
Add a session-scoped article cache with a 15-minute TTL (matching Anthropic's prompt cache TTL is a useful mental model):

```python
_article_cache: dict = {}  # {client_name: (timestamp, articles)}
_ARTICLE_CACHE_TTL = 900   # 15 minutes

def _get_or_fetch_articles(client_categories, client_name):
    now = time.time()
    cached = _article_cache.get(client_name)
    if cached and (now - cached[0]) < _ARTICLE_CACHE_TTL:
        return cached[1]
    articles = fetch_articles(client_categories)
    _article_cache[client_name] = (now, articles)
    return articles
```

**Pillar(s):** Energy · Hardware  
**Green Software Pattern:** Demand Shaping — avoid redundant network I/O

**Business outcome:** For a user asking 5 questions in a session, reduces RSS fetch operations from 5×20+ = 100+ HTTP requests to 20+ total. Significant latency improvement on follow-up questions (no 3–5s RSS wait).

---

## Slide 9 — Solution 4: Instrumentation Layer

**Problem:** Zero telemetry in the codebase. No token counts, no latency per call, no cost-per-R. Without a baseline, no improvement can be proven — and no "green" claim can be made honestly.

**Change:**  
Add a `@track_call` decorator wrapping every `client.messages.create()` call:

```python
def track_call(purpose: str):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            resp = fn(*args, **kwargs)
            ms = int((time.perf_counter() - t0) * 1000)
            _log_call(purpose, resp.usage.input_tokens,
                      resp.usage.output_tokens, ms, resp.model)
            return resp
        return wrapper
    return decorator
```

Write to SQLite `llm_telemetry` table. Add a hidden `/metrics` Panel tab showing calls/R, cost/R trend, cache hit rate.

**Pillar(s):** Measurement  
**Green Software Pattern:** Measure Application Energy Consumption

**Business outcome:** Unlocks every other improvement. Gives CTO a cost-per-session number. Required before any honest green claim.

---

## Slide 10 — Measurement Plan

**What to track for 2 weeks post-instrumentation:**

| Metric | How to collect | Success threshold |
|---|---|---|
| Tokens per strategy R (input + output) | `@track_call` → SQLite `llm_telemetry` | Baseline week 1; track change |
| API calls per strategy R | Counter in telemetry | <5 calls/R after cache (from 7 today) |
| Latency per strategy R (ms) | Start/end timestamps in telemetry | <30s P95 (from ~40s today) |
| Strategy cache hit rate | Hit/miss flag in telemetry | >40% within 2 weeks for returning users |
| Cost per strategy R ($) | tokens × published API pricing | Baseline then -30% target in 4 weeks |
| Icarus query RSS fetches per session | HTTP call counter | <20 per session (from 20+ per question) |

**What counts as success:**  
Cache hit rate >40% AND cost/R trending down after 2 weeks = first honest, measurement-backed green claim.

**SCI framing:**  
`SCI = (E × I + M) / R`  
- E proxy: tokens × model energy estimate (available via ML CO₂ impact estimates)  
- I: grid intensity for Anthropic/xAI inference — **not yet disclosed, cannot publish SCI score**  
- M: device emissions — out of scope for API-only service  
- R: one strategy package  

We will not publish an SCI score until I is confirmed.

---

## Slide 11 — Caveats & Honesty

**What we will NOT claim:**

- "SpendLens is carbon neutral" — no carbon data. Greenwashing.
- "Each strategy costs X gCO₂" — Anthropic/xAI inference region grid intensity not publicly disclosed.
- "We reduced carbon by Y%" — without before/after measurement, this is a hypothesis.
- "Model right-sizing reduced energy" — already done (Haiku was already in use). Cannot claim this as a new saving.

**v1 audit errors we corrected in this version:**  
The original audit named supplier profiler batching, category mapper caching, and Icarus batching as solutions — all three were already implemented. Publishing those as "improvements" would have been inaccurate. Auditing the actual code before presenting findings matters.

**Offsets vs SCI (lesson reminder):**  
Buying carbon offsets does NOT lower your SCI score. SCI measures real energy and embodied carbon per functional unit. Offsets are accounted separately.

**What we WILL validate next:**  
1. Add `@track_call` instrumentation (1 day)  
2. Run 2-week baseline before any optimisation  
3. Request region disclosure from Anthropic  
4. Rerun this audit with real numbers

**Stakeholder ask:** Approve 1-day instrumentation sprint before any other green initiative.

---

## Slide 12 — Before/After Hypothesis

**If we implement Solutions 1–4:**

| Change | Hypothesis | Metric to watch (1 week) |
|---|---|---|
| Strategy cache (TTL 7d) | ~60–80% fewer strategy chain executions for returning users | Cache hit rate in telemetry |
| Haiku for Icarus query/weekly (after quality eval) | ~15× token cost reduction per query/summary | Cost/R for Icarus calls |
| Session-scoped article cache (15min TTL) | ~80% fewer RSS HTTP requests for multi-question sessions | Icarus fetch count per session |
| Instrumentation layer | All other metrics now trackable; baseline established | Data completeness % |

**Combined hypothesis:**  
> "If all four changes are shipped, we expect cost-per-R for strategy generation to drop 60–70% within 4 weeks, and cost-per-Icarus-query to drop ~90% within the same window — without measurable degradation in output quality (validated by 5-sample eval for Haiku migration)."

**This is a hypothesis, not a claim.** We present actual numbers after the 2-week measurement window.

---

*Deck v2 — updated after code review of the actual SpendLens source*  
*Lab: Ironhack Week 6 LAB 10 — Green Software & Sustainable AI*  
*Path: B — Green Retrofit Audit | Artifact: eugnmueller-87/PROCUREMENT*
