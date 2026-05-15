# Autonomous Procurement Request Triage Agent

## What problem does this solve?

Every company processes purchase requests (PRs) daily — from a $50 office supply order to a $500k software contract. Today this is almost entirely manual:

- Someone checks if the supplier has a valid NDA, DPA, and MSA
- The request gets forwarded by email to the right approver
- A category manager manually identifies suppliers, writes RFQ/RFP documents, sends emails, chases responses, compares quotes in Excel
- For large purchases, the requester has to write a business case from scratch
- A PO gets created manually in the ERP after everything is done

This process is slow, error-prone, and scales poorly. Category managers spend most of their time on administrative triage instead of strategic sourcing.

**This agent automates the entire flow** — from the moment a PR lands, to supplier compliance checking, to routing, to RFQ/RFP outreach, to collecting quotes, to notifying the right people at every step.

---

## How it works — the tier model

Every purchase request is automatically classified into one of five tiers based on value:

| Request Value | Path | What happens |
|---|---|---|
| < €5,000 | Auto-approve | Budget checked, PO created in ERP, requester notified — no human involved |
| €5k – €25k | Cost center head approval | Manager receives email with approve/reject links, requester notified of outcome |
| €25k – €50k | RFQ (min. 2 suppliers) | Category manager reviews, agent sends RFQ to shortlisted suppliers, collects quotes, generates comparison matrix |
| €50k – €100k | RFQ+ (min. 3 suppliers) | Same as above with formal scoring and stricter evaluation |
| > €100k | Full RFP + Business Case | Agent guides requester through a structured business case, Category Manager initiates RFP to 3+ suppliers, market analysis generated, evaluation matrix built |

Before any path proceeds, the agent checks the supplier database for valid **NDA, DPA, and MSA** contracts. Missing or expired agreements block the process and flag the issue automatically.

---

## Architecture

The system is split into two layers that communicate via HTTP:

- **LangGraph** (Python) — the reasoning brain. Handles tier classification, supplier compliance checks via RAG over ChromaDB, business case Q&A, document generation, and evaluation matrices.
- **n8n** (6 workflows) — the integration layer. Handles all I/O: webhooks from the P2P tool, email sending via SMTP, ERP API calls, supplier outreach, and approval link handling.

```
P2P Tool → n8n Webhook → LangGraph Agent → n8n (email / ERP / outreach)
```

---

## The 6 n8n Workflows

### Workflow 1 — PR Ingestion

![PR Ingestion](Screenshots/1.%20PR%20ingetion.png)

**What it automates:** The entry point for every purchase request.

When a PR is submitted in the P2P tool, a webhook fires into n8n. The workflow:

1. **Receives the PR** via POST webhook
2. **Validates all required fields** — `pr_id`, `requester_name`, `requester_email`, `description`, `category`, `amount`, `currency`, `cost_center` — and throws a descriptive error if anything is missing
3. **Forwards the parsed PR** to the LangGraph agent via HTTP, which classifies the tier and runs the supplier compliance check
4. **Builds an audit log entry** with the tier decision and agent reasoning
5. **Responds to the P2P tool** with a confirmation including the PR ID and assigned tier

Before this agent, someone had to manually read the PR, figure out who to send it to, and check supplier contracts by searching through shared drives. This workflow replaces all of that in under 2 minutes.

---

### Workflow 2 — Notification & Approval Routing

![Notification Routing](Screenshots/2.%20Notification%20routing.png)

**What it automates:** Getting the right email to the right person immediately after tier classification.

The LangGraph agent calls back to this workflow with the routing decision. A **Switch node** branches into 5 paths based on the tier:

- **Auto-approve** → SMTP email to the requester confirming approval and PO number
- **Cost center approval** → SMTP email to the cost center head with a full PR summary table and one-click **Approve / Reject** buttons linked to Workflow 6
- **RFQ** → SMTP email to the Category Manager with PR details, supplier compliance report, and suggested supplier shortlist
- **RFQ+** → Same as RFQ but flagged as requiring a minimum of 3 suppliers and formal scoring
- **RFP** → SMTP email to the requester explaining that a business case is required before sourcing can begin, with a guided list of what will be asked

Before this agent, routing happened over email chains that took hours or days. This workflow fires within seconds of the PR being submitted.

---

### Workflow 3 — ERP Integration

![ERP Integration](Screenshots/3%20ERP%20integration.png)

**What it automates:** Budget checks and purchase order creation — the two touchpoints with the ERP system.

The LangGraph agent calls this workflow with one of two actions:

- **Budget check** → The stub queries synthetic cost center budget data and returns: available budget, whether it covers the request, and the cost center head's name and email (used in Workflow 2 to address the approval email correctly)
- **Create PO** → The stub generates a PO number, records the order, and returns confirmation back to LangGraph

Both branches return their results to the LangGraph agent via HTTP callback so the reasoning flow can continue.

> **MVP note:** Both ERP nodes are stubs implemented as Code nodes with synthetic data. In production, replace them with HTTP Request nodes pointing to your ERP's REST API (SAP, Oracle, etc.). The rest of the workflow stays identical.

Before this agent, budget checks required someone to log into the ERP, look up the cost center, and create the PO manually — a process that could take 30+ minutes per request.

---

### Workflow 4 — Supplier Outreach (RFQ / RFP)

![Supplier Outreach](Screenshots/4%20Supplier%20outreach.png)

**What it automates:** Sending RFQ and RFP documents to suppliers and chasing non-responses.

This workflow has two independent branches:

**Top branch — outreach trigger:**
1. LangGraph calls the webhook with the CM-approved supplier shortlist and the generated RFQ/RFP document
2. A **Code node splits** the supplier list into individual items — one per supplier
3. Each supplier receives a **personalised SMTP email** with the RFQ or RFP document attached, their contact name, submission deadline, and a link to submit their response
4. An **outreach log** is built recording which suppliers were contacted and when
5. LangGraph is **notified** that outreach is complete and the waiting period has begun

**Bottom branch — automated reminders:**
- A **Schedule trigger** runs every business day at 09:00
- Checks for supplier responses that are overdue
- Sends a reminder email automatically to any supplier who hasn't responded

Before this agent, a category manager would spend 1–2 hours per RFQ writing individual supplier emails, tracking who responded in a spreadsheet, and manually sending follow-ups. This workflow handles all of it.

---

### Workflow 5 — Quote & Proposal Collection

![Quote Collection](Screenshots/5%20Quote%20collection.png)

**What it automates:** Receiving supplier responses and tracking completeness.

When a supplier submits a quote or proposal (via the response link from Workflow 4):

1. **Webhook receives** the supplier response
2. **Parser normalises** the response — extracts price, delivery days, payment terms, validity, and notes regardless of how the supplier formatted their submission
3. **LangGraph receives** the structured data, extracts key evaluation fields, and updates the comparison matrix in its state
4. **Completeness check** — the Code node asks LangGraph whether all expected suppliers have now responded
5. **Switch branches:**
   - If **all responded** → SMTP email to the Category Manager: "All quotes received, evaluation matrix ready — click here to review"
   - If **still waiting** → SMTP acknowledgement to the submitting supplier: "Thank you, we are still awaiting X other responses"

Before this agent, quotes arrived by email in different formats, had to be manually copied into an Excel comparison sheet, and someone had to track who had and hadn't responded. This workflow closes that loop automatically.

---

### Workflow 6 — Approval Response Handling

![Approval Response](Screenshots/6%20Approval%20response.png)

**What it automates:** Processing the cost center head's approve/reject decision and closing the loop with the requester.

The approval email from Workflow 2 contains two one-click links. When the cost center head clicks either:

1. **Webhook receives** the GET request with `pr_id`, `decision`, and `approver` as query parameters
2. **Parser validates** the decision and extracts fields
3. **Browser confirmation page** is immediately returned to the approver — they see "Response Recorded, you can close this window" without having to navigate anywhere
4. **Switch branches on decision:**
   - **Approved path** → LangGraph is notified → triggers ERP PO creation (Workflow 3) → requester receives SMTP email with approval confirmation and PO number
   - **Rejected path** → LangGraph is notified → PR is closed → requester receives SMTP email with rejection reason and guidance on resubmission

Before this agent, approval decisions were sent by reply email, someone had to read them, manually update the PR status, create the PO, and separately notify the requester. This workflow makes the entire chain happen from a single click.

---

## Technology Stack

| Component | Technology |
|---|---|
| Agent framework | LangGraph (Python) |
| RAG / supplier compliance | LangChain + ChromaDB |
| LLM | Claude Sonnet 4.6 (Anthropic) |
| Workflow orchestration | n8n (self-hosted) |
| Email | SMTP |
| Supplier database | Synthetic JSON → ChromaDB (25–30 suppliers) |
| ERP integration | Stubbed Code nodes (replace with HTTP in production) |

---

## Repository Structure

```
WEEK 4/LAB4/
├── README.md                          ← this file
├── project_plan.md                    ← full project plan with architecture, risk assessment, implementation phases
├── lab_summary.md                     ← reflection: hardest part, what to do differently, open questions
├── n8n_workflows/
│   ├── workflow_1_pr_ingestion.json
│   ├── workflow_2_notifications_routing.json
│   ├── workflow_3_erp_integration.json
│   ├── workflow_4_rfq_supplier_outreach.json
│   ├── workflow_5_quote_collection.json
│   └── workflow_6_approval_response.json
└── Screenshots/
    ├── 1. PR ingetion.png
    ├── 2. Notification routing.png
    ├── 3 ERP integration.png
    ├── 4 Supplier outreach.png
    ├── 5 Quote collection.png
    └── 6 Approval response.png
```

---

## How to import the workflows into n8n

1. Open n8n → **Workflows** → **Import from file**
2. Import each JSON file from the `n8n_workflows/` folder one by one
3. Go to **Settings → Credentials** and create an SMTP credential named exactly `SMTP Account`
4. In every workflow, update the **HTTP Request nodes** — replace `http://localhost:8000` with the actual URL where your LangGraph agent is running
5. Activate all 6 workflows

> The workflows are connected via webhooks. Workflow 1 is the entry point — trigger it by sending a POST request with a purchase request payload to start the full flow.

---

## Webhook endpoints summary

| Workflow | Method | Path | Called by |
|---|---|---|---|
| 1 — PR Ingestion | POST | `/webhook/pr-ingestion` | P2P tool |
| 2 — Notifications | POST | `/webhook/routing-decision` | LangGraph agent |
| 3 — ERP | POST | `/webhook/erp-request` | LangGraph agent |
| 4 — Supplier Outreach | POST | `/webhook/send-rfq` | LangGraph agent |
| 5 — Quote Collection | POST | `/webhook/supplier-response` | Supplier (via link) |
| 6 — Approval Response | GET | `/webhook/approval-response` | Approver (via email link) |
