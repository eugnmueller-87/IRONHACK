# Autonomous Procurement Agent — Project Plan

## 1. Use Case

### Problem Statement
Enterprise procurement teams receive purchase requests (PRs) through a P2P (Procure-to-Pay) tool ranging from small office supplies to six-figure software contracts. Today, routing, supplier checks, RFQ/RFP initiation, and business case creation are largely manual — category managers spend significant time on administrative triage rather than strategic sourcing.

### Solution
An autonomous procurement agent that ingests PRs from the P2P tool, applies tier-based routing logic, enforces supplier compliance checks, guides requesters through business case elaboration for high-value purchases, and orchestrates the appropriate sourcing process (auto-approve → approval → RFQ → RFP).

### Target Users
- **Requesters** — employees submitting purchase requests
- **Cost Center Heads** — approving mid-range requests ($5k–$25k)
- **Category Managers** — overseeing RFQ/RFP processes and supplier selection
- **Finance / Procurement Ops** — monitoring spend, compliance, and PO creation

### Current Manual Process
1. Requester submits PR in P2P tool
2. Someone manually checks if supplier is approved and contracts are in place
3. Request routed by email to approver
4. Category manager manually identifies suppliers, sends RFQ/RFP emails
5. Quotes collected, compared in Excel
6. Award decision made, PO manually created in ERP

### Success Criteria
- PRs < $5k processed without human touch in < 2 minutes
- Supplier compliance check runs automatically on every request
- Business case completeness rate > 90% for requests > $100k before CM review
- Category managers spend < 15 min on RFQ initiation vs. current ~2 hours
- Full audit trail for every routing decision

---

## 2. Technology Stack

### Selected Technologies

| Component | Technology | Role |
|---|---|---|
| Core LLM | Claude Sonnet 4.6 (Anthropic) | Reasoning, business case Q&A, document generation |
| Agent Framework | LangGraph | Tier routing state machine, multi-step workflow orchestration |
| RAG | LangChain + ChromaDB | Supplier database queries (NDA/DPA/MSA checks, compliance status) |
| Embeddings | OpenAI text-embedding-3-small | Supplier and contract document embeddings |
| Orchestration | n8n | P2P webhook ingestion, ERP API calls, email outreach, notifications |
| Supplier Database | Synthetic JSON/CSV → ChromaDB | Approved supplier master with contract status |
| Document Generation | LLM + Markdown → PDF | Business case and RFQ/RFP document output |

### Justification

**LangGraph over plain LangChain agent:**
The tier routing is a branching state machine with 5 distinct paths, conditional transitions, and human-in-the-loop checkpoints. LangGraph's explicit node/edge model makes this auditable and debuggable. A plain ReAct agent would produce unpredictable branching.

**RAG over hardcoded lookups:**
Supplier compliance data will grow over time and category managers need to query it in natural language ("Does Vendor X have a valid DPA?"). Embedding the supplier master into ChromaDB enables both structured lookups and semantic search.

**n8n for orchestration:**
All external system integrations (P2P webhook, ERP REST API, email to suppliers) are best handled in n8n — low-code, visual, easy to maintain by non-developers. The LangGraph agent focuses on reasoning; n8n handles I/O.

**Claude Sonnet 4.6:**
Strong reasoning for business case elaboration, good at structured document generation, and cost-effective for the volume of requests expected.

### Alternatives Considered

| Alternative | Reason Not Selected |
|---|---|
| GPT-4o | Claude performs better on long structured document tasks; cost similar |
| Pinecone | ChromaDB is free, local, sufficient for MVP supplier DB size |
| Airflow | Too heavy for MVP; n8n covers scheduling and webhooks with less ops overhead |
| Simple LangChain agent | Cannot model explicit human-in-the-loop checkpoints reliably |

---

## 3. MVP Scope

### Tier Model

| Request Value | Path | Agent Behavior |
|---|---|---|
| < $5k | Auto-approve | Budget check → PO trigger in ERP → notify requester |
| $5k – $25k | Cost center head approval | Route to manager with PR summary → track response → PO or decline |
| $25k – $50k | RFQ (2+ suppliers) | Route to Category Manager → CM approves supplier shortlist → agent sends RFQ → quote comparison matrix |
| $50k – $100k | RFQ+ (3+ suppliers) | Same as above, more formal scoring, stricter evaluation |
| > $100k | Full RFP + Business Case | Business case builder → Category Manager review → RFP to 3 suppliers → market analysis → evaluation matrix → award recommendation |

### Included in MVP

- PR ingestion via n8n webhook (simulating P2P tool)
- Tier classification based on request value
- Supplier compliance check (NDA, DPA, MSA, approved status) via RAG over synthetic DB
- Auto-approval flow (< $5k): budget check + ERP PO creation stub + notification
- Cost center head routing ($5k–$25k): email notification + approval tracking
- Category Manager routing ($25k+): PR summary + supplier shortlist suggestion
- RFQ flow ($25k–$100k): agent sends RFQ email to 2–3 suppliers, collects responses, generates comparison matrix
- Business case builder (> $100k): guided conversational Q&A with requester, structured PDF output
- RFP flow (> $100k): RFP document generation, 3-supplier outreach, evaluation matrix, award recommendation
- Synthetic supplier database: 20–30 suppliers across categories with contract status, ratings, contacts
- Full audit log of every routing decision and action taken

### Out of Scope (v2+)

- Live ERP integration (stubbed in MVP — simulated API responses)
- Live P2P tool integration (n8n webhook simulates incoming PRs)
- Negotiation automation (CM handles negotiations; agent provides talking points only)
- Multi-language support
- Mobile interface
- Spend analytics dashboard
- Supplier onboarding workflow (adding new suppliers to the database)
- Contract lifecycle management post-award

### Success Metrics

| Metric | MVP Target |
|---|---|
| Correct tier routing accuracy | > 95% on test PRs |
| Supplier compliance check coverage | 100% of PRs checked |
| Business case completeness (> $100k) | All 9 required fields populated |
| Auto-approval end-to-end time | < 2 minutes |
| RFQ email generation quality | Category manager rating ≥ 4/5 |

---

## 4. Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| LLM hallucination in business case Q&A | Medium | High | Structured output with validation, required fields enforced, CM reviews before proceeding |
| RAG miss on supplier compliance check | Low | High | Fallback to "no contract found = blocked" (safe default), manual override by procurement ops |
| n8n webhook reliability | Low | Medium | Retry logic in n8n, dead-letter queue for failed PR ingestions |
| LangGraph state corruption on long RFP flows | Medium | Medium | Persist state to database at each node, enable resume from last checkpoint |
| LLM API costs exceeding budget | Medium | Medium | Cache frequent supplier queries, use cheaper model for classification step, set spend alerts |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Category managers don't trust agent recommendations | High | High | Show full reasoning trail, always keep CM as decision-maker, never auto-award above $25k |
| Requesters bypass agent (email direct to CM) | Medium | Medium | Process change management, make agent faster than the old way |
| Scope creep during build | High | Medium | Strict MVP boundary, defer all v2 items, weekly scope review |
| Compliance gap (agent misses a required contract) | Low | High | Legal review of compliance rules before go-live, conservative defaults |

### Data Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Synthetic supplier DB not representative enough | Medium | Medium | Model it on real procurement categories (IT, facilities, marketing, professional services) |
| Supplier contact emails bounce during RFQ | Low | Low | Use placeholder email domain for MVP, real validation in v2 |
| Budget data from ERP stub is inaccurate | Low | Medium | Clearly label ERP calls as simulated in MVP, validate integration in v2 |

---

## 5. Implementation Plan

### Phase 1 — Foundation (Week 1)

**Goal:** Infrastructure, synthetic data, and routing logic working end-to-end.

| Task | Description |
|---|---|
| Synthetic supplier DB | Create 25–30 suppliers across 4 categories (IT software, IT hardware, professional services, facilities). Include NDA/DPA/MSA status, expiry dates, approved status, contact, past performance rating. |
| ChromaDB setup | Embed supplier records, test RAG queries for compliance lookups |
| LangGraph skeleton | Define all 5 tier nodes, routing edges, and state schema |
| n8n webhook | Set up PR ingestion workflow, parse request fields, trigger LangGraph agent |
| Tier routing tests | 20 test PRs covering all tiers and edge cases (boundary values, missing fields) |

### Phase 2 — Core Agent Logic (Week 2)

**Goal:** All tier paths functional with supplier compliance check.

| Task | Description |
|---|---|
| Supplier compliance node | RAG lookup for NDA/DPA/MSA, return structured compliance report |
| Auto-approval flow | Budget check (ERP stub) → PO creation stub → requester notification |
| Cost center head routing | Email notification template, approval tracking in n8n |
| Category manager routing | PR summary generation, supplier shortlist from RAG |
| RFQ document generator | LLM generates RFQ from PR details + supplier category |

### Phase 3 — RFP & Business Case Builder (Week 3)

**Goal:** High-value request path fully functional.

| Task | Description |
|---|---|
| Business case Q&A flow | 9-question guided conversation, state tracked in LangGraph |
| Business case PDF output | Structured document from Q&A answers |
| RFP document generator | Formal RFP from business case + PR details |
| Supplier evaluation matrix | Score 3 suppliers on price, delivery, compliance, rating |
| Market analysis stub | LLM generates brief category market overview as context for CM |
| Award recommendation | Ranked supplier recommendation with reasoning |

### Phase 4 — Integration & Testing (Week 4)

**Goal:** Full end-to-end flows tested, demo-ready.

| Task | Description |
|---|---|
| End-to-end flow tests | Run 10+ scenarios covering each tier |
| Audit log | Every decision logged with timestamp, actor, reasoning |
| Error handling | Graceful failures for missing data, API timeouts, supplier non-response |
| Demo setup | 5 representative PR scenarios for showcase (one per tier) |
| Documentation | README, architecture diagram, demo script |

### Timeline Summary

| Phase | Duration | Key Milestone |
|---|---|---|
| Phase 1 | Week 1 | Routing logic + supplier DB working |
| Phase 2 | Week 2 | All 5 tiers routing correctly with compliance check |
| Phase 3 | Week 3 | Business case builder + RFP flow complete |
| Phase 4 | Week 4 | Full demo-ready system with audit trail |

---

## 6. Synthetic Supplier Database Design

### Schema

```json
{
  "supplier_id": "SUP-001",
  "name": "Acme Software GmbH",
  "category": "IT Software",
  "region": "DACH",
  "status": "preferred",
  "nda": { "exists": true, "expiry": "2026-12-31" },
  "dpa": { "exists": true, "expiry": "2026-12-31" },
  "msa": { "exists": true, "expiry": "2027-06-30" },
  "contact_name": "Anna Müller",
  "contact_email": "anna.mueller@acme-software.example.com",
  "past_performance_rating": 4.2,
  "notes": "Preferred vendor for SaaS tools, strong data security posture"
}
```

### Categories Covered (MVP)
- IT Software (8 suppliers)
- IT Hardware (6 suppliers)
- Professional Services / Consulting (7 suppliers)
- Facilities & Office (5 suppliers)

### Statuses
- `preferred` — approved, all contracts valid, go-to supplier
- `approved` — approved, contracts may be expiring soon
- `conditional` — missing one contract (e.g., no DPA yet), can engage with CM approval
- `blocked` — do not engage (legal/compliance issue or poor performance)

---

## 7. Business Case Builder — Question Set (> $100k)

For **tool/software purchases**, the agent asks:

1. What business problem does this tool solve?
2. Who are the primary users and how many?
3. What is the expected annual contract value and total contract duration?
4. Who is the business owner (accountable) and IT owner (technical)?
5. Does this tool process, store, or transfer personal data? *(triggers DPA requirement)*
6. What is the implementation scope — internal team, vendor-led, or hybrid?
7. What existing systems does this need to integrate with?
8. What is the target go-live date and key milestones?
9. What is the cost of not purchasing this tool (status quo risk)?

For **services/consulting purchases**, questions 6–8 are replaced with:
- What are the deliverables and acceptance criteria?
- What is the expected duration and resourcing model?
- Who from our side will manage the engagement?

---

## 8. Architecture Diagram

```
P2P Tool
    │
    ▼ (webhook)
n8n Workflow
    │  parse PR fields
    ▼
LangGraph Agent
    │
    ├─ Supplier Compliance Node ──► ChromaDB (RAG)
    │         │
    │    [compliance report]
    │         │
    ▼         ▼
  Tier Router
    │
    ├─ < $5k ──────────► Auto-Approve Node ──► ERP stub (PO) ──► Notify
    │
    ├─ $5k–$25k ────────► Cost Center Approval Node ──► n8n email ──► Track
    │
    ├─ $25k–$50k ───────► Category Manager Node
    │                          │
    │                    RFQ Node ──► Supplier shortlist (RAG)
    │                          │       ──► RFQ email (n8n)
    │                          │       ──► Quote collection
    │                          └────► Comparison matrix ──► CM decision
    │
    ├─ $50k–$100k ──────► Same as above, 3 suppliers, formal scoring
    │
    └─ > $100k ─────────► Business Case Builder Node (guided Q&A)
                               │
                         Business Case PDF
                               │
                         Category Manager Review
                               │
                         RFP Node ──► 3 suppliers (n8n)
                               │       ──► Response collection
                               │       ──► Market analysis (LLM)
                               └────► Evaluation matrix ──► Award recommendation
                                                                │
                                                         CM awards ──► PO in ERP
```

---

## 9. n8n Workflow Design

n8n is the integration layer — it handles all I/O with external systems so the LangGraph agent can focus purely on reasoning. The two communicate via HTTP: n8n calls the LangGraph agent as an HTTP node, and LangGraph calls back to n8n webhook endpoints to trigger outbound actions.

### Workflow 1 — PR Ingestion (Entry Point)

**Trigger:** Webhook POST from P2P tool (or manual trigger for MVP demo)

```
[Webhook] → [Parse PR fields] → [Validate required fields]
    │
    ▼
[HTTP node: POST to LangGraph agent]
    │
    ▼
[Log PR received + agent response to audit table]
```

**Fields extracted from P2P payload:**
- `pr_id`, `requester_name`, `requester_email`
- `description`, `category`, `preferred_supplier`
- `amount`, `currency`, `cost_center`
- `urgency`, `required_by_date`

---

### Workflow 2 — Notifications & Approval Routing

**Trigger:** Webhook called by LangGraph when a routing decision is made

```
[Webhook: routing_decision]
    │
    ├─ tier = "auto_approve"
    │       └─ [Send email to requester: approved + PO number]
    │
    ├─ tier = "cost_center_approval"
    │       └─ [Send email to Cost Center Head with PR summary + approve/reject links]
    │       └─ [Set reminder: re-notify if no response in 48h]
    │
    ├─ tier = "rfq" or "rfq_plus"
    │       └─ [Send email to Category Manager: PR summary + suggested supplier shortlist]
    │       └─ [Attach compliance report from RAG]
    │
    └─ tier = "rfp"
            └─ [Send email to requester: business case required]
            └─ [Send email to Category Manager once business case complete]
```

---

### Workflow 3 — ERP Integration (Budget Check & PO Creation)

**Trigger:** HTTP call from LangGraph auto-approve node

```
[Webhook: erp_request]
    │
    ├─ action = "budget_check"
    │       └─ [HTTP GET: ERP budget API (stubbed)]
    │       └─ [Return: available_budget, cost_center_owner]
    │
    └─ action = "create_po"
            └─ [HTTP POST: ERP PO endpoint (stubbed)]
            └─ [Return: po_number, confirmation]
            └─ [Log PO to audit table]
```

**MVP note:** ERP endpoints are stubbed — n8n returns realistic mock responses so the LangGraph flow can be tested end-to-end without a live ERP connection.

---

### Workflow 4 — RFQ / RFP Supplier Outreach

**Trigger:** Webhook called by LangGraph once CM approves supplier shortlist

```
[Webhook: send_rfq]
    │
    ├─ [Loop over supplier list]
    │       └─ [Send email to supplier contact with RFQ/RFP PDF attached]
    │       └─ [Log: supplier notified, timestamp]
    │
    └─ [Set follow-up reminder: 5 business days]
            └─ [If no response: send reminder email]
            └─ [If still no response after 3 days: notify CM]
```

---

### Workflow 5 — Quote / Proposal Collection

**Trigger:** Webhook POST from supplier reply (or manual upload for MVP)

```
[Webhook: supplier_response]
    │
    ├─ [Attach file to PR record]
    │
    └─ [HTTP node: POST to LangGraph]
            └─ [Agent extracts: price, delivery, terms, deviations]
            └─ [Updates evaluation matrix in state]
            └─ [If all suppliers responded: notify CM for award decision]
```

---

### Workflow 6 — Approval Response Handling

**Trigger:** Cost Center Head clicks approve/reject link in email

```
[Webhook: approval_response]
    │
    ├─ response = "approved"
    │       └─ [HTTP node: notify LangGraph → trigger ERP PO creation]
    │       └─ [Email requester: approved]
    │
    └─ response = "rejected"
            └─ [HTTP node: notify LangGraph → close PR]
            └─ [Email requester: rejected + reason field]
```

---

### n8n ↔ LangGraph Integration Pattern

```
n8n (I/O layer)                    LangGraph (reasoning layer)
─────────────────                  ──────────────────────────
Webhook receives PR        ──►     Ingest node classifies + routes
                           ◄──     Returns: tier, compliance_report
Send approval email        ◄──     Cost center approval node
Webhook receives response  ──►     Resume from approval checkpoint
Send RFQ emails            ◄──     RFQ node (after CM shortlist approval)
Webhook receives quotes    ──►     Quote extraction + matrix update node
Send award notification    ◄──     Award recommendation node
Create PO in ERP           ◄──     Auto-approve or final award node
```

**Key principle:** LangGraph never sends emails or calls external APIs directly. It always calls back to n8n via HTTP, keeping all integrations in one maintainable place.

---

## 10. Resources Needed

### Team (MVP)
| Role | Responsibility |
|---|---|
| AI Engineer | LangGraph agent, RAG setup, LLM prompt engineering |
| n8n Developer / Integration | Webhook, ERP stub, email workflows |
| Procurement SME | Validate tier logic, business case questions, compliance rules |
| Category Manager (tester) | UAT on RFQ/RFP flows |

### Services & Tools
| Service | Purpose | Cost Estimate (MVP) |
|---|---|---|
| Anthropic API (Claude Sonnet 4.6) | LLM inference | ~$20–$50/month (MVP volume) |
| ChromaDB | Vector store | Free (local) |
| n8n | Workflow orchestration | Free (self-hosted) or ~$20/month (cloud) |
| GitHub | Version control | Free |

### Budget Considerations
- MVP can be built and run for < $100/month in API costs at low volume
- Scale cost estimate: at 500 PRs/month with avg. 10 LLM calls per PR → ~$500/month
- Main cost driver: business case builder Q&A (long conversations) — implement caching for repeated question patterns
