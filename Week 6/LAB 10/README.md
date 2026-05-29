# LAB 10 — Defend Your Stack's Carbon Story

![Week](https://img.shields.io/badge/Week-6-2E7D32?style=flat-square)
![Lab](https://img.shields.io/badge/Lab-10-1B5E20?style=flat-square)
![Path](https://img.shields.io/badge/Path-B%20Retrofit%20Audit-A5D6A7?style=flat-square&logoColor=white)
![Pillars](https://img.shields.io/badge/GSF%20Pillars-Carbon%20%7C%20Energy%20%7C%20Hardware%20%7C%20Measurement-388E3C?style=flat-square)
![Slides](https://img.shields.io/badge/Slides-12%20content%20%2B%20title-66BB6A?style=flat-square)
![Artifact](https://img.shields.io/badge/Artifact-SpendLens-1B5E20?style=flat-square)

**Ironhack AI Engineering Bootcamp | Week 6**  
**Author:** Eugen Mueller  
**Path:** B — Green Retrofit Audit of an existing artifact

---

## What this lab covers

A GSF-aligned green software audit of **SpendLens** — a production-quality AI-powered procurement intelligence platform built during this bootcamp. The audit applies the four Green Software Foundation pillars (Carbon, Energy, Hardware, Measurement) to identify hotspots, propose concrete improvements, and define an honest measurement plan.

**Artifact audited:** `eugnmueller-87/PROCUREMENT` — SpendLens  
**Audience:** CTO / Head of Engineering considering SaaS productisation  
**Functional unit (R):** One complete Category Strategy package delivered per user session

---

## Files

| File | Description |
|---|---|
| [SpendLens_Green_Audit_LAB10.pptx](SpendLens_Green_Audit_LAB10.pptx) | Primary deliverable — 13-slide deck (title + 12 content slides) |
| [deck_spendlens_green_audit.md](deck_spendlens_green_audit.md) | Full deck content in Markdown — all slide text, speaker notes, and reasoning |
| [appendix_audit_table.md](appendix_audit_table.md) | Retrofit audit template + lever table + full GSF pillar coverage map |
| [generate_deck.py](generate_deck.py) | Python script that generates the PPTX from scratch using python-pptx |

---

## Deck outline (12 content slides)

| # | Slide | Key content |
|---|---|---|
| 1 | Hook | SpendLens use case; why green software matters; business risk tiers |
| 2 | One Unit of Value (R) | R = one complete strategy package; why R is the billing unit |
| 3 | Hotspots | 5 hotspots ranked by severity; skeptical stakeholder challenge answered |
| 4 | Assumptions | 5 honest guesses; explicit uncertainty; what to validate first |
| 5 | Pillars Map | 2×2 showing how hotspots touch Carbon / Energy / Hardware / Measurement |
| 6 | Solution 1 | Semantic response cache (Energy · Carbon) |
| 7 | Solution 2 | Model right-sizing — Sonnet vs Haiku tiering (Energy · Carbon · Hardware) |
| 8 | Solution 3 | Batched supplier profiler — O(n) → O(n/20) (Energy · Hardware) |
| 9 | Solution 4 | Instrumentation layer — measurement first (Measurement) |
| 10 | Measurement Plan | 5 metrics, how to collect, success thresholds; SCI framing |
| 11 | Caveats | No greenwashing; offsets ≠ SCI; what we won't claim; next steps |
| 12 | Before/After Hypothesis | Combined hypothesis: -50–65% cost/R if all 4 changes ship |

---

## GSF Pillar coverage

| Pillar | Solutions |
|---|---|
| Carbon | Region disclosure; SCI framing |
| Energy | Semantic cache; model right-sizing; Icarus session cache |
| Hardware | Batched supplier profiler; demand shaping |
| Measurement | @track_call instrumentation layer (prerequisite for all other pillars) |

---

## Green Software Patterns referenced

- Static Assets / Demand Shaping (Solution 1 — cache)
- Optimize AI Model (Solution 2 — model right-sizing)
- Batch AI Requests (Solution 3 — supplier profiler)
- Measure Application Energy Consumption (Solution 4 — instrumentation)

---

## Honesty statement

No unverifiable "carbon neutral" claims are made. All quantitative hypotheses are labelled as estimates pending a 2-week instrumentation baseline. Grid intensity (I in SCI) is not claimed until Anthropic/xAI discloses inference region data.
