# Eugen Mueller — AI Engineering Portfolio

4-week intensive AI engineering bootcamp at Ironhack, plus independent full-stack projects.  
Focus: autonomous agents, RAG pipelines, LangChain, LangGraph, n8n workflow automation, and real-world AI applications.

---

## Featured Projects

### Autonomous Procurement Triage Agent
**[WEEK 4 / LAB4](WEEK%204/LAB4/)** · LangGraph · LangChain · ChromaDB · n8n · Claude Sonnet 4.6 · SMTP

An end-to-end autonomous agent that replaces manual procurement triage. Purchase requests arrive from a P2P tool and are automatically routed through 5 value-based tiers — from instant auto-approval to full RFP processes with business case elaboration, supplier compliance checks, and multi-supplier outreach.

**What it automates:**
- Supplier contract compliance checks (NDA, DPA, MSA) on every request via RAG over a supplier database
- Tier routing: auto-approve (<€5k) → cost center approval → RFQ (2–3 suppliers) → full RFP + business case (>€100k)
- Guided business case Q&A for high-value tool/software purchases
- RFQ/RFP document generation and personalised SMTP email outreach to suppliers
- Quote collection, evaluation matrix, and award recommendation
- One-click approve/reject for managers with automatic ERP PO creation

**6 n8n workflows** fully built and importable. LangGraph handles all reasoning; n8n handles all I/O.

---

### Kita Connect
**[github.com/eugnmueller-87/kita-connect](https://github.com/eugnmueller-87/kita-connect)** · Next.js · Supabase · n8n · Claude Haiku · Vercel

A full-stack daycare management platform for German Kitas (daycare centers), engineered to run at near-zero monthly cost (~€0/month). Built to unify the fragmented tools parents and educators currently use — separate WhatsApp groups, paper forms, email threads — into one GDPR-compliant platform.

**Three portals in one:**
- **Parents** — secure child development documentation, direct messaging with educators, multi-language support (German, English, Russian)
- **Educators** — observation tracking (Sismik, Seldak, Perik assessments), AI-assisted learning stories via Claude Haiku, milestone tracking, broadcast announcements
- **Management** — multi-channel communication (in-app, email, Telegram, SMS), automated registration and support ticket workflows, GDPR compliance

**Key engineering decisions:** Supabase for free-tier PostgreSQL with row-level security and realtime, Vercel for frontend hosting, n8n self-hosted for GDPR-compliant automation, Resend for 3,000 free emails/month. All infrastructure hosted in Frankfurt (EU) region.

Currently in active development — Phase 1 (infrastructure + n8n automation) in progress.

---

## Bootcamp Labs by Week

### Week 1 — Python & AI Foundations
| Lab | What it covers |
|---|---|
| [LAB5](WEEK%201/LAB5/) | Python scripting fundamentals, data processing |

---

### Week 2 — LangChain & RAG
| Lab | What it covers |
|---|---|
| [LAB 2.2](WEEK%202/LAB%202.2/) | RAG pipeline basics — chunking, embedding, retrieval |
| [LAB 3](WEEK%202/LAB%203/) | Python refactoring lab — modular design, error handling |
| [LAB 4](WEEK%202/LAB%204/) | LangChain agents — tool use, ReAct pattern |
| [EXTRA](WEEK%202/EXTRA/) | Extended RAG exercises |

---

### Week 3 — Advanced Agents
| Lab | What it covers |
|---|---|
| [LAB 2](WEEK%203/LAB%202/) | **NormalObjects Creative Complaint Handler** — LangChain agent with 4 custom tools, free tool selection |
| [LAB 3](WEEK%203/LAB%203/) | **Relevance Scoring & Rerankers** — RAG pipeline over EU AI Act + podcast transcripts, Cohere reranking, LLM relevance scoring |
| [LAB 4](WEEK%203/LAB%204/) | **Bloyce's Protocol (LangGraph)** — strict 5-step complaint workflow: intake → validate → investigate → resolve → close |

---

### Week 4 — Autonomous Agents & n8n
| Lab | What it covers |
|---|---|
| [LAB1](WEEK%204/LAB1/) | **NormalObjects LangGraph** — deterministic complaint processor with fixed workflow graph |
| [LAB2](WEEK%204/LAB2/) | **n8n Node Analysis** — systematic study of 20 node types across 3 class workflows |
| [LAB4](WEEK%204/LAB4/) | **Autonomous Procurement Triage Agent** ← featured project above |
| [EXTRA 2](WEEK%204/EXTRA%202/) | **arXiv Research Summarizer** — n8n + Claude + Notion pipeline: fetch paper → summarise → store |
| [EXTRA 3](WEEK%204/EXTRA%203/) | **Error Handling & Scheduled Workflows** — n8n retry logic, error branches, idempotent daily scheduler |

---

## Tech Stack Across This Repo

| Technology | Used in |
|---|---|
| Python | All weeks |
| LangChain | Week 2 LAB 4, Week 3 LAB 2, Week 3 LAB 4 |
| LangGraph | Week 3 LAB 4, Week 4 LAB1, Week 4 LAB4 |
| RAG / ChromaDB / Upstash | Week 2, Week 3 LAB 3, Week 4 LAB4 |
| n8n | Week 4 LAB2, LAB4, EXTRA 2, EXTRA 3 |
| Claude (Anthropic) | Week 4 LAB4, EXTRA 2 |
| OpenAI | Week 2–4 |
| Notion API | Week 4 EXTRA 2 |
| MCP (Model Context Protocol) | Week 3 LAB 4 |
| Next.js / Supabase | Kita Connect |

---

## Connect

- GitHub: [github.com/eugnmueller-87](https://github.com/eugnmueller-87)
- Bootcamp: Ironhack AI Engineering — Berlin, 2026
