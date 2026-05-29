# SpendLens — Path B Retrofit Audit Template (v2 — Code-Verified)
### Appendix to: deck_spendlens_green_audit.md

---

## Artifact
**SpendLens — AI-Powered Procurement Intelligence Platform**  
Repo: `eugnmueller-87/PROCUREMENT`  
Modules audited (source read): `icarus.py`, `category_strategy.py`, `supplier_profiler.py`, `category_mapper.py`  
Audit version: v2 — corrects v1 assumptions by reading actual code

---

## Primary User Journey
User uploads a spend CSV → SpendLens normalises and categorises rows (category_mapper.py) → User selects a category and clicks "Generate Strategy" → 7 sequential Haiku calls (Kraljic → PESTEL → SWOT → Porter's → TCO → Levers → Recommendation) → Returns full strategy package in ~40 seconds. Separately: User triggers Icarus scan or query → 20+ parallel RSS fetches + optional 4 Grok calls + batched Haiku analysis OR 1 Sonnet call for targeted query.

**R (functional unit):** One complete category strategy package delivered per user session.

---

## What v1 Assumed vs. What the Code Actually Does

| v1 assumption | Reality (from source) | Impact on audit |
|---|---|---|
| All 8 strategy calls use Sonnet | `_call_claude()` uses `claude-haiku-4-5-20251001` for all 7 frameworks | Solution 2 (model right-sizing) already done |
| Supplier profiler: 1 Claude call per supplier row | `supplier_profiler.py` has zero LLM calls — pure rule-based ABC/scoring | Not a hotspot |
| Category mapper re-runs on re-upload | `category_mapper.py` has `vendor_cache.json` — only new vendors hit Claude | Not a hotspot |
| Icarus: 1 Claude call per article | `analyze_with_claude()` batches 15 articles/call, 5 parallel workers | Already optimised |
| Icarus RSS: sequential fetches | `ThreadPoolExecutor(max_workers=len(RSS_SOURCES))` — all feeds parallel | Already optimised |

---

## Lever Table (Corrected)

| Lever | Current state (code-verified) | Better alternative |
|---|---|---|
| **Strategy result cache** | `generate_all_frameworks()` runs 7 Haiku calls every time, no freshness check | Hash-based SQLite cache keyed on `(client_name + category + spend_hash)`, TTL 7 days. `load_strategy()` already exists — extend with freshness gate |
| **Model for Icarus query/weekly** | `query_with_claude` and `weekly_summary` use `claude-sonnet-4-6` for structured JSON extraction | Downgrade to `claude-haiku-4-5-20251001` after 5-sample quality eval — structured JSON output is Haiku's strongest use case |
| **Icarus session article cache** | `fetch_articles()` called inside every `query_with_claude` — re-fetches 20+ RSS feeds per question | Module-level dict cache `{client_name: (timestamp, articles)}` with 15-min TTL; trivial to add |
| **Instrumentation** | Zero telemetry — no tokens, no latency, no cost/R tracked anywhere | `@track_call` decorator on `client.messages.create()` + SQLite `llm_telemetry` table + `/metrics` Panel tab |

---

## Hotspots (Verified)

| # | Hotspot | File | Evidence | Severity |
|---|---|---|---|---|
| 1 | Strategy 7-call chain, no cache | `category_strategy.py:418` `generate_all_frameworks()` | Sequential steps list, no TTL/freshness check | HIGH |
| 2 | Icarus query re-fetches RSS every call | `icarus.py:833` `query_with_claude()` | `fetch_articles()` called unconditionally at top of function | HIGH |
| 3 | Sonnet for structured JSON extraction | `icarus.py:882, 958` | `model="claude-sonnet-4-6"` in `query_with_claude` and `weekly_summary` | MEDIUM |
| 4 | 4 Grok clusters per big scan regardless of scope | `icarus.py:653` `_fetch_grok_articles()` | All 4 clusters queried even if user has 1–2 categories | MEDIUM |
| 5 | Zero telemetry | All files | No logging of `usage.input_tokens`, no latency tracking | CRITICAL |

---

## Green Opportunities (Prioritised)

1. **[Quick win — 1 day]** Add `@track_call` instrumentation → SQLite `llm_telemetry`. Enables all other improvements. Zero functional change.

2. **[Quick win — 2 days]** Strategy result cache — extend `load_strategy()` with `generated_at` freshness check + hash of spend data. Skip 7 Haiku calls on cache hit.

3. **[Quick win — 1 day]** Module-level article cache in `icarus.py` — 15-min TTL dict. Eliminates redundant RSS re-fetches within a session.

4. **[Medium — 2 days]** Downgrade `query_with_claude` and `weekly_summary` to Haiku after 5-sample quality eval. Two-line code change, one day of eval.

5. **[Medium — 1 day]** Scope Grok cluster calls to only clusters that overlap with client's active categories — skip clusters with no matching categories entirely.

6. **[Strategic — post-SaaS]** Region-aware deployment: route inference to low-carbon region when Anthropic/xAI expose grid-aware endpoints.

---

## What I Would Measure to Prove Improvement

| Metric | Tool | Baseline target |
|---|---|---|
| Tokens per strategy R | `@track_call` → `llm_telemetry` | Establish week 1; compare week 3 |
| API calls per strategy R | Counter in telemetry | <5 after cache (from 7 today) |
| Strategy cache hit rate | Hit/miss flag | >40% within 2 weeks |
| Latency per strategy R (ms) | Start/end timestamps | <30s P95 |
| Cost per strategy R ($) | tokens × pricing | -30% within 4 weeks |
| Icarus RSS fetches per session | HTTP call counter in `_fetch_feed` | <20 per session (from 20+/question) |

---

## Risks / Tradeoffs

| Risk | Mitigation |
|---|---|
| Strategy cache staleness — market conditions change | 7-day TTL + "Refresh Strategy" button to bypass cache |
| Haiku quality regression for complex RFP briefs | Run 5-sample eval; keep Sonnet for `generate_rfp_brief` if needed |
| Article cache returns stale signals for urgent queries | 15-min TTL short enough for real-time feel; add "Force refresh" option |
| Grok scoping skips a cluster that had an edge-case relevant article | Accept: better to miss one article than to run 4 full cluster queries for a 1-category client |
| Instrumentation adds latency | Async SQLite write; measured overhead <1ms |

---

## GSF Pillar Coverage

| Pillar | Solutions addressing it |
|---|---|
| Carbon | Region disclosure (strategic), SCI framing in measurement plan |
| Energy | Strategy cache (S1), Haiku downgrade for query/weekly (S2), Grok scoping (S5) |
| Hardware | Session article cache reduces I/O (S3), Grok scoping reduces API calls (S5) |
| Measurement | Instrumentation layer (S4) — prerequisite for all other pillars |

---

## v1 → v2 Correction Log

| v1 solution | Status in v2 |
|---|---|
| Model right-sizing: tier Sonnet vs Haiku for strategy | **REMOVED** — Haiku already used for all 7 strategy frameworks |
| Batched supplier profiler | **REMOVED** — no LLM calls in supplier_profiler.py |
| Strategy cache | **KEPT** — confirmed not yet implemented |
| Instrumentation layer | **KEPT** — confirmed zero telemetry |
| Icarus session cache (new in v2) | **ADDED** — discovered by reading `query_with_claude()` |
| Haiku for Icarus query/weekly (new in v2) | **ADDED** — discovered Sonnet usage in `query_with_claude` and `weekly_summary` |

---

*Appendix v2 — updated after code review of SpendLens source*  
*Lab: Ironhack Week 6 LAB 10 — Green Software & Sustainable AI*
