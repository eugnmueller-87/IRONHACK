# News Summariser — Multi-Provider Edition

A production-ready pipeline that fetches live news, summarises each article with OpenAI, and analyses sentiment with Anthropic Claude — all while tracking costs and respecting rate limits.

---

## File map

| File | Purpose |
|---|---|
| `config.py` | Loads `.env`, exposes all settings, validates required keys |
| `news_api.py` | Fetches headlines from newsapi.org with rate limiting |
| `llm_providers.py` | Unified interface to OpenAI + Anthropic; cost tracker; fallback logic |
| `summarizer.py` | Orchestrates the two-step pipeline; async variant included |
| `main.py` | Interactive CLI entry point |
| `test_summarizer.py` | Full unit-test suite (all external calls mocked) |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template — copy to `.env` and fill in real keys |

---

## Setup

```bash
# 1. Clone / navigate to this folder
# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API keys
cp .env.example .env
# Edit .env and replace the placeholder values
```

You need three API keys:

- **OpenAI** — platform.openai.com
- **Anthropic** — console.anthropic.com
- **NewsAPI** — newsapi.org (free tier is fine)

---

## How to run

```bash
# Interactive mode
python main.py

# Smoke-test individual modules
python config.py          # validates keys
python news_api.py        # fetches 3 articles
python llm_providers.py   # tests both LLMs + fallback
python summarizer.py      # full pipeline on 2 articles

# Run the test suite
pytest test_summarizer.py -v
```

---

## Example output (truncated)

```
================================================================================
NEWS SUMMARY REPORT
================================================================================

1. OpenAI releases GPT-5 with improved reasoning
   Source: TechCrunch | Published: 2026-04-30T10:00:00Z
   URL: https://techcrunch.com/...

   SUMMARY:
   OpenAI unveiled GPT-5 today, claiming significant improvements in
   multi-step reasoning and code generation. The model is available via
   API immediately, with consumer rollout planned for next month.

   SENTIMENT:
   Overall sentiment: Positive (85% confidence). The tone is enthusiastic
   and optimistic, reflecting excitement about a major product launch.

================================================================================
COST SUMMARY
================================================================================
Total requests:           4
Total cost:               $0.0023
Total tokens:             3,812
  Input:                  2,901
  Output:                 911
Average cost per request: $0.000575
================================================================================
```

---

## Cost analysis

| Provider | Model | Input ($/M) | Output ($/M) | Typical cost / article |
|---|---|---|---|---|
| OpenAI | gpt-4o-mini | $0.15 | $0.60 | ~$0.0001 |
| Anthropic | claude-3-5-sonnet | $3.00 | $15.00 | ~$0.0010 |

Processing **500 articles/day** costs roughly **$0.55/day** — well under the $5 default budget.

---

## Architecture

```
NewsAPI  ──►  article text
                  │
                  ▼
             OpenAI gpt-4o-mini   ──►  2-3 sentence summary
                  │
                  ▼
        Anthropic claude-3-5-sonnet  ──►  sentiment + confidence
                  │
                  ▼
             Report + cost summary
```

Fallback: if OpenAI fails, Anthropic handles both steps. If both fail, the article is skipped and processing continues.
