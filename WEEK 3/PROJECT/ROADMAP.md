# Hermes Agent — Roadmap

## Vision

Hermes is Icarus's external intelligence layer and SpendLens's live data source. While Icarus manages your personal world (calendar, email, tasks), Hermes watches the external world — tech suppliers, AI companies, markets, research — and makes that intelligence available on demand. Together they form a complete personal operations system: one facing inward, one facing outward, and SpendLens using both.

---

## Phase 1 — Deploy & Stabilize ✅ COMPLETE

Get Hermes running reliably in production.

- [x] Remove Telegram notifier (Hermes is pull-only, Icarus is master)
- [x] Create `hermes-agent` GitHub repository
- [x] Deploy to Railway as a new service alongside Icarus
- [x] Set environment variables on Railway
- [x] Verify RSS, Tavily, and EDGAR crawlers run on schedule
- [x] Confirm Redis keys are written correctly in `hermes:*` namespace

**Status:** Live on Railway. RSS crawls every 6h, EDGAR daily at 07:30, Tavily weekly Monday 09:00. Redis connection verified. All sensitive keys excluded from version control.

---

## Phase 1b — SpendLens Integration ✅ COMPLETE

Hermes feeds procurement intelligence directly into SpendLens.

- [x] Build `HermesClient` — standalone connector with fuzzy vendor name matching
- [x] `get_procurement_briefing()` — top significant procurement signals across all suppliers
- [x] `enrich_vendor_list()` — bulk risk scoring (HIGH/MEDIUM/LOW) for a list of vendors
- [x] `to_icarus_signals()` — converts Hermes items to Icarus signal format with category/relevance/impact mapping
- [x] Inject Hermes signals into SpendLens Icarus pipeline (prepended before Claude analysis)
- [x] Add Hermes context to SpendLens `query_with_claude()` prompt
- [x] `upstash-redis` added to SpendLens requirements; credentials shared via `.env`

**Status:** SpendLens pulls Hermes procurement signals on every analysis cycle automatically. Integration is fail-safe — returns empty list if Redis is unreachable.

---

## Phase 1c — Miro Agent ✅ COMPLETE

Turn Hermes data into visual Miro boards, triggerable from Telegram.

- [x] Miro API access (OAuth token, correct scopes: boards:read, boards:write)
- [x] `miro/client.py` — REST API wrapper (boards, frames, sticky notes, cards)
- [x] `miro/boards.py` — Signal board (items grouped by signal type, colour-coded urgency)
- [x] `miro/boards.py` — Landscape board (suppliers as cards grouped by category, tier-coloured)
- [x] FastAPI HTTP server added to `main.py` — `POST /miro/landscape` and `POST /miro/signals`
- [x] `HERMES_API_KEY` authentication on all Miro endpoints
- [x] Wire Miro board creation to Icarus Telegram (via `hermes` skill in Icarus)

**Status:** Full pipeline live. Say "build a Miro board" in Telegram → Icarus calls Hermes HTTP endpoint → board is created → URL returned to you.

---

## Phase 2 — Icarus Integration (On-Demand Queries) ✅ COMPLETE

Icarus learns to pull from Hermes when you ask.

- [x] Add `hermes` skill to Icarus (`bot/skills/hermes.py`)
- [x] `hermes_query` — "what does Hermes have on [company]?" → pulls `hermes:supplier:{slug}` with fuzzy matching
- [x] `hermes_briefing` — "give me a Hermes briefing" → top significant signals across all suppliers
- [x] `build_miro_board` — "build a Miro board" → calls Hermes HTTP endpoint, returns URL
- [x] Icarus system prompt updated with Hermes tool usage rules
- [x] `HERMES_URL` and `HERMES_API_KEY` added to Icarus environment

**Status:** All three tools live in Icarus. Natural language triggers work end-to-end. Requires `HERMES_URL` to be set in Icarus Railway env to the Hermes service URL.

---

## Phase 3 — Knowledge Layer (Procurement + AI Skillset)

Hermes builds structured, growing knowledge about each company — not just news items but a living profile.

- [ ] Design company profile schema (funding history, key products, pricing, risk flags, recent signals)
- [ ] Populate profiles incrementally as crawlers find new data
- [ ] Separate procurement intelligence (pricing, supply chain, distributors) from AI intelligence (models, benchmarks, funding)
- [ ] Store profiles at `hermes:profile:{slug}` in Redis
- [ ] Icarus can ask "what do we know about Cerebras?" and get a full profile, not just recent news

**Success criteria:** Each tracked company has a growing knowledge profile. Icarus can give you a supplier brief without needing to search the web.

---

## Phase 4 — Autonomous Intelligence

Hermes operates with minimal input, surfacing what matters without being asked.

- [ ] Icarus morning briefing enriched with top Hermes signals (opt-in, pulled by Icarus at 06:00)
- [ ] Weekly Hermes digest — auto-generated summary of the week's most significant signals per category
- [ ] Auto-generate Miro board on major events (large funding round, major acquisition) — triggered by Icarus
- [ ] SpendLens deeper integration — Hermes supplier profiles feed SpendLens vendor detail views
- [ ] Supplier watchlist — track specific companies with higher frequency on demand

**Success criteria:** The system surfaces the right intelligence at the right time with minimal prompting. Icarus remains the decision layer throughout.

---

## Architecture Principles (Preserved Across All Phases)

1. **Icarus is master** — Hermes never pushes, never accesses personal data, never sends Telegram messages
2. **Shared Redis, separate namespaces** — `hermes:*` is Hermes territory, everything else is Icarus
3. **Pull on demand** — Icarus and SpendLens fetch Hermes data when needed, not on a push schedule
4. **Least privilege** — each agent knows only what it needs to do its job
5. **Railway as single platform** — Icarus and Hermes run as separate Railway services in one project
6. **SpendLens is a consumer** — not a master agent; it reads from the same Redis pipe as Icarus
