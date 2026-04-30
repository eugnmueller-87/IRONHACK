# TLDR — News Summariser Lab

## What it does
Fetches live news → summarises with OpenAI → analyses sentiment with Anthropic → prints a cost report. Handles provider failures with automatic fallback.

## Key files (read these first)
1. **`config.py`** — all settings in one place, loaded from `.env`
2. **`llm_providers.py`** — the two LLM clients + `CostTracker` + fallback logic
3. **`summarizer.py`** — the pipeline: article in → summary + sentiment out
4. **`main.py`** — CLI wrapper around the pipeline

## Run it in 3 commands
```bash
pip install -r requirements.txt
cp .env.example .env   # then add your real API keys
python main.py
```

## Test it in 1 command
```bash
pytest test_summarizer.py -v   # no real API keys needed — all calls are mocked
```

## Cost at a glance
~$0.55/day for 500 articles. OpenAI handles cheap summarisation; Anthropic handles nuanced sentiment. If OpenAI fails, Anthropic does both.

## Pipeline diagram
```
NewsAPI → raw article
         ↓
     OpenAI (summarise)
         ↓
     Anthropic (sentiment)
         ↓
     Report + cost summary
```
