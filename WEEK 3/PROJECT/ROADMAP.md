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

**Status:** SpendLens now queries Hermes Redis on every analysis cycle. Verified with `Hermes connected — 0 procurement signals available` (correct — Hermes has been running for a short time). Signals will flow through automatically as Redis data accumulates.

---

## Phase 1c — Miro Agent ✅ BUILT

Turn Hermes data into visual Miro boards.

- [x] Miro API access (OAuth token, correct scopes: boards:read, boards:write)
- [x] `miro/client.py` — REST API wrapper (boards, frames, sticky notes, cards)
- [x] `miro/boards.py` — Signal board (items grouped by signal type, colour-coded urgency)
- [x] `miro/boards.py` — Landscape board (suppliers as cards grouped by category, tier-coloured)
- [ ] Wire Miro board creation to Icarus Telegram commands (Phase 4)

**Status:** Miro modules built and ready. Boards will be fully useful once Hermes has accumulated more Redis data. Telegram trigger is the remaining step.

---

## Phase 2 — Icarus Integration (On-Demand Queries)

Icarus learns to pull from Hermes when you ask.

- [ ] Add Telegram command handler in Icarus for Hermes queries
- [ ] `"What does Hermes have on [company]?"` → pulls `hermes:supplier:{slug}`
- [ ] `"Any AI signals today?"` → filters items by category + date
- [ ] `"What's moving in semiconductors?"` → category-level digest
- [ ] `"Give me a Hermes briefing"` → top 5 significant signals of the day
- [ ] Icarus formats Hermes data cleanly before showing it (no raw JSON)

**Success criteria:** You can ask Icarus about any tracked company or category from Telegram and get a clean, formatted answer sourced from Hermes data.

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

## Phase 4 — Miro Agent — Telegram Trigger

Wire the built Miro Agent to Icarus so boards can be triggered from chat.

- [ ] Add Telegram command handler in Icarus for Miro board requests
- [ ] `"Build a board for chip suppliers"` → Miro competitive landscape, returns URL
- [ ] `"Map today's Hermes signals"` → visual signal board, returns URL
- [ ] `"Create a presentation on AI infrastructure"` → Miro presentation board
- [ ] Miro Agent pulls from Hermes data, does not access personal Icarus data

**Success criteria:** You can trigger a Miro board from Telegram in under 60 seconds, populated with real Hermes data.

---

## Phase 5 — Autonomous Intelligence

Hermes and the Miro Agent operate with minimal input, surfacing what matters without being asked.

- [ ] Icarus morning briefing enriched with top Hermes signals (opt-in, not a push from Hermes)
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
5. **Railway as single platform** — Icarus, Hermes, Miro Agent all run as separate Railway services in one project
6. **SpendLens is a consumer** — not a master agent; it reads from the same Redis pipe as Icarus
