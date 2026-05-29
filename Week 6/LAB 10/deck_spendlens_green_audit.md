# SpendLens Carbon Story — Green Software Audit Deck
### Path B — Green Retrofit Audit
**Eugen Mueller | Ironhack AI Engineering Bootcamp | Week 6 LAB 10**

---

## Slide 1 — Hook

**Artifact:** SpendLens — AI-Powered Procurement Intelligence Platform  
**Audience:** CTO / Head of Engineering considering SaaS productisation

**Why green software matters here:**  
SpendLens runs multiple LLM API chains per user session — live Grok searches, parallel RSS fetches, 5–8 sequential Claude calls to generate a full category strategy package. At current call patterns, a single "Generate Strategy" click costs roughly the same in tokens and latency as ~30 simple chat turns.  
As SpendLens moves from prototype to multi-tenant SaaS, compute cost, API spend, and carbon exposure all scale linearly with users — unless we fix the architecture first.

> **Risk tiers:** cost overrun (API spend), latency regression (user churn), brand risk (sustainability claims without measurement).

---

## Slide 2 — One Unit of Value (R)

**R = one complete Category Strategy package delivered per user session**

That package includes:
- Kraljic quadrant classification
- PESTEL analysis
- SWAT analysis
- Porter's Five Forces
- TCO breakdown
- Negotiation levers narrative
- 3-year roadmap
- 10-slide HTML deck export

**Why R matters here:**  
R is the billing unit. Every improvement we propose will be measured as *change in resource consumption per R* — not per API call, not per token batch.  
If we halve the calls-per-R, we halve cost and carbon exposure even with user growth.

---

## Slide 3 — Assessment Defense: Hotspots

**Where compute concentrates today:**

| Hotspot | Description | Pattern |
|---|---|---|
| Category Strategy chain | 5–8 sequential Claude API calls (Kraljic → PESTEL → SWAT → Porter's → TCO → Levers → Roadmap → Deck) | Sequential, no cache |
| Icarus RSS fetch | Parallel fetch across 10+ RSS feeds per session trigger | High I/O, data movement |
| Icarus analysis chain | Grok live search + Claude synthesis per market brief | Redundant if same category re-queried within session |
| Supplier profiler | Claude call per supplier row, no batch window | O(n) unbatched calls |
| Category mapper | Embedding/classification per upload — re-runs on re-upload of same file | No deduplication |

**Repeated work (caching candidates):**  
- Same category queried multiple times per session → Icarus re-fetches same RSS feeds  
- Same CSV uploaded twice → category mapper re-classifies identical rows  
- Strategy package re-generated for unchanged spend data → full 8-call chain re-runs  

> *Skeptical stakeholder: "How do you know these are the real hotspots?"*  
> Honest answer: We do not have instrumentation yet. These are structural inferences from reading the code. Slide 10 defines the measurement plan to validate or overturn them.

---

## Slide 4 — Assessment Defense: Assumptions

**Five honest guesses — what we do not know yet:**

1. **API region:** Claude API and Grok API calls are routed to Anthropic/xAI infrastructure. We do not know which AWS/GCP region handles inference — grid carbon intensity varies 3–10× between US-East (coal-heavy) and EU-West (renewables-heavy).

2. **Model size:** We call `claude-sonnet-4-5` (strategy chain) — a large frontier model. We have not tested whether a smaller model (Haiku) produces acceptable output quality for simpler subtasks like PESTEL bullet generation.

3. **Call frequency:** We assume a power user runs 2–4 full strategy generations per week. At 8 calls × 4 runs = 32 Claude calls/week. If batch frequency is higher or multi-tenant, this multiplies fast.

4. **Token counts:** Average prompt+response per strategy call estimated at ~3,000–6,000 tokens. Not instrumented. Could be 2× higher due to full spend data passed as context.

5. **Retention / idle compute:** Panel dashboard is served locally today; no always-on server cost. In SaaS mode, idle container cost becomes real.

**What we would validate first:** token count per call (cheapest to measure — add logging tomorrow).

---

## Slide 5 — Pillars Map

**How SpendLens hotspots touch the four GSF pillars:**

```
                    CARBON
                    ├── Unknown inference region → unknown grid intensity
                    └── No SCI score tracked today

         ENERGY                          HARDWARE
         ├── 8 sequential LLM calls      ├── Supplier profiler: O(n) calls, no batching
         │   per R — no parallelism      ├── Category mapper: re-runs on re-upload
         ├── Icarus: redundant           └── No demand-shaping (run at off-peak?)
         │   RSS fetches
         └── No caching layer

                    MEASUREMENT
                    ├── Zero telemetry today (tokens, latency, cost/R)
                    ├── No carbon proxy metric defined
                    └── Cannot claim improvement without baseline
```

**Priority order:** Measurement first (needed to prove everything else) → Energy (biggest quick wins) → Hardware (medium effort) → Carbon (longer-term, requires infra control).

---

## Slide 6 — Solution 1: Semantic Response Cache

**Problem:** Category Strategy chain re-runs 8 LLM calls even when the underlying spend data and category selection have not changed since last session.

**Change:**  
Implement a hash-based cache keyed on `(category_name + spend_data_hash + model_id)`.  
Cache strategy output (JSON) in SQLite with a 7-day TTL.  
On cache hit: skip the full chain, serve cached result in <100ms.

**Pillar(s):** Energy · Carbon  
**Green Software Pattern:** [Static Assets](https://patterns.greensoftware.foundation/catalog/web/use-a-cdn) (serve pre-computed results instead of recomputing) / Demand Shaping

**Business outcome:** ~60–80% reduction in API calls for repeat users; direct cost reduction in Claude API spend; latency drops from ~45s to <1s for cached strategies.

**Tradeoff:** Stale cache risk if market conditions change. Mitigated by TTL + manual "Refresh" button.

---

## Slide 7 — Solution 2: Model Right-sizing (Tiered Calls)

**Problem:** All 8 strategy subtasks use the same large Sonnet model — including simple formatting tasks (bullet list expansion, roadmap table formatting) that don't require frontier capability.

**Change:**  
- Keep Sonnet for high-reasoning subtasks: Kraljic classification, Porter's competitive analysis, Negotiation Levers  
- Downgrade to Haiku for structured-output subtasks: PESTEL bullet expansion, SWOT table fill, TCO row generation  
- Add a 5-sample quality eval before shipping (compare Haiku vs Sonnet output on 5 historical categories)

**Pillar(s):** Energy · Carbon · Hardware  
**Green Software Pattern:** [Optimize AI Model](https://patterns.greensoftware.foundation/catalog/ai/optimize-ai-model)

**Business outcome:** Haiku is ~15× cheaper per token than Sonnet. If 4 of 8 calls can move to Haiku, estimated 40–50% cost reduction per R — without compromising decision quality on the high-stakes outputs.

**Caveat:** Never a blind downgrade — quality gate required. State this on every model-size recommendation.

---

## Slide 8 — Solution 3: Batched Supplier Profiler

**Problem:** Supplier profiler issues one Claude API call per supplier row — for a spend file with 200 suppliers, that is 200 sequential calls, one at a time.

**Change:**  
Batch suppliers into groups of 10–20 per API call using a structured JSON prompt (`classify these 15 suppliers: [...]`).  
Use Claude's tool_use / JSON mode to return structured results per batch.  
Reduces 200 calls → ~12–20 calls for the same output.

**Pillar(s):** Energy · Hardware  
**Green Software Pattern:** [Batch Processing](https://patterns.greensoftware.foundation/catalog/ai/batch-ai-requests)

**Business outcome:** 10× reduction in API call count for supplier classification. Faster completion (parallel batch calls vs. sequential). Significant API cost reduction for large customer files.

---

## Slide 9 — Solution 4: Instrumentation Layer (Measurement First)

**Problem:** We cannot prove any improvement without a baseline. Zero telemetry exists today — no token counts, no latency per call, no cost-per-R.

**Change:**  
Add a lightweight `@track_call` decorator wrapping every LLM call:
```python
# logs: timestamp, model, prompt_tokens, completion_tokens, latency_ms, call_purpose
track_call(model="claude-sonnet-4-5", purpose="kraljic_classification", ...)
```
Write to SQLite `llm_telemetry` table. Add a hidden `/metrics` Panel tab showing:
- Calls per R (this session)
- Estimated cost per R (using published API pricing as proxy)
- Token trend over last 30 days

**Pillar(s):** Measurement  
**Green Software Pattern:** [Measure Application Energy Consumption](https://patterns.greensoftware.foundation/catalog/operational/measure-application-energy-consumption)

**Business outcome:** Unlocks every other improvement. Gives CTO a cost-per-customer-session number to put in front of investors. Required before any "green" claim can be made honestly.

---

## Slide 10 — Measurement Plan

**What to track for 2 weeks post-instrumentation:**

| Metric | How to collect | Success threshold |
|---|---|---|
| Tokens per R (input + output) | `@track_call` decorator → SQLite | Baseline established; then -20% after cache |
| API calls per R | Count in telemetry table | <5 calls/R after batching (from ~8+ today) |
| Latency per R (ms) | Start/end timestamp per strategy run | <30s P95 (from ~45s today) |
| Cache hit rate | Cache hit/miss flag in telemetry | >40% within 2 weeks for repeat users |
| Cost per R ($ proxy) | tokens × published pricing | Tracked weekly; target -30% within 4 weeks |

**What counts as success:**  
A 2-week run showing cache hit rate >40% AND cost/R trending down — that is the first honest, measurement-backed green claim we can make.

**SCI framing:**  
`SCI = (E × I + M) / R`  
We can partially operationalize: E proxy = tokens × model energy estimate; I = grid intensity (requires region disclosure from Anthropic/xAI); M = device emissions (out of scope for API-only service). R = one strategy package.  
We will not publish an SCI score until I (grid intensity) is confirmed.

---

## Slide 11 — Caveats & Honesty

**What we will NOT claim:**

- "SpendLens is carbon neutral" — we have no carbon data yet. This would be greenwashing.
- "Each strategy costs X gCO₂" — grid intensity for Anthropic and xAI inference regions is not publicly disclosed at this time.
- "We reduced carbon by Y%" — without a before/after measurement, this is a hypothesis, not a result.

**Offsets vs SCI (lesson reminder):**  
Buying carbon offsets does not lower your SCI score. SCI measures real energy and embodied carbon per functional unit — offsets are accounted separately and do not substitute for efficiency work.

**What we WILL validate next:**  
1. Add `@track_call` instrumentation (1 day of work)  
2. Run 2-week baseline before any optimisation  
3. Disclose region to Anthropic support or monitor CF-aware API billing when available  
4. Rerun this assessment with real numbers — update deck

**Stakeholder ask:** Approve 1-day instrumentation sprint before any other green initiative. Without measurement, all other improvements are guesses.

---

## Slide 12 — Before/After Hypothesis

**If we implement Solutions 1–4:**

| Change | Hypothesis | Metric to watch (1 week) |
|---|---|---|
| Semantic cache (TTL 7 days) | ~60% fewer strategy chain executions for repeat users | Cache hit rate in telemetry |
| Model right-sizing (Haiku for 4/8 subtasks) | ~40% reduction in token cost per R | Cost/R in telemetry |
| Batched supplier profiler (20/batch) | ~90% fewer supplier API calls per upload | Supplier calls/upload |
| Instrumentation layer | Baseline established; all other metrics now trackable | Data completeness % |

**Combined hypothesis:**  
> "If all four changes are shipped, we expect cost-per-R to drop by 50–65% within 4 weeks, with no measurable degradation in strategy output quality (validated by 5-sample Haiku eval)."

**This is a hypothesis, not a claim.** We will present actual numbers after the 2-week measurement window.

---

*Deck prepared for: Ironhack AI Engineering Bootcamp — Week 6 LAB 10*  
*Path: B — Green Retrofit Audit of existing project artifact*  
*Artifact: SpendLens (eugnmueller-87/PROCUREMENT)*
