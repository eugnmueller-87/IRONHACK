# LAB 3 — Relevance Scoring and Rerankers

Advanced RAG pipeline for querying EU AI Act legal text and Trustworthy AI podcast transcripts, with LLM-based relevance scoring and Cohere reranking.

## Files

| File | Description |
|------|-------------|
| `relevance_scoring_rerankers.ipynb` | Main notebook — all 7 steps |
| `lab_summary.md` | Summary of when reranking helps and when to use it |
| `README.md` | This file |

## How to Run

1. Install dependencies (first notebook cell runs `%pip install` automatically)
2. OpenAI key and Upstash credentials are pre-filled in the notebook
3. Add the document URLs provided by your TA in the **Step 1a** cell:
   - `PODCAST_TRANSCRIPT_URL`
   - `EU_AI_ACT_PDF_URL`
4. Run all cells top to bottom

No Cohere key needed — reranking uses the free local `cross-encoder/ms-marco-MiniLM-L-6-v2` model (~70 MB, downloaded once automatically).

Upstash Vector index is pre-configured (EU1 region, 1536 dims, cosine metric).

## Pipeline Overview

```
Documents (EU AI Act PDF + Podcast Transcripts)
    ↓  chunk with metadata (source, page, section, doc_type)
    ↓  embed with OpenAI text-embedding-3-small
    ↓  store in Upstash Vector
    
Query
    ↓  embed query
    ↓  retrieve top-10 by vector similarity  ← baseline
    ↓  metadata filter (eu_ai_act / podcast_transcript)
    ↓  Cohere rerank → top-5               ← advanced
    ↓  LLM relevance scoring (GPT)          ← advanced
    ↓  GPT-4o-mini generates answer
```

## Key Results

See `relevance_scoring_rerankers.ipynb` Step 7 for before/after comparison tables and the position-shift analysis showing which chunks reranking promotes vs demotes.
