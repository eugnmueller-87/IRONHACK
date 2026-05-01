# TLDR — LAB 5: Chunking Strategies

## What was built
A Jupyter notebook that implements and compares 4 chunking strategies on two real documents:
- **PDF:** EU AI Ethics Guidelines (`ethics_guidelines_for_trustworthy_ai...pdf`, 195,243 chars)
- **Audio:** Trustworthy AI podcast (`The_Blueprint_For_Trustworthy_AI.m4a`) — transcribed via Whisper (28.8 MB split into 2 segments → 16,427 chars)

## Results

| Strategy | PDF chunks | Podcast chunks | Mid-sentence breaks (PDF) |
|---|---|---|---|
| Fixed-Size (1000, overlap 100) | 217 | 20 | 96.3% — very poor |
| Recursive Char (1000, overlap 200) | 258 | 22 | 66.7% — good |
| Token-Based (500t, overlap 50) | 162 | 10 | n/a (token-level) |
| Semantic (sample only, threshold 0.75) | 32 | 32 | best coherence |

## Recommendations
- **PDF → Recursive Character** (`chunk_size=1000`, `overlap=200`): respects paragraph and sentence structure, lowest mid-sentence break rate
- **Podcast → Token-Based** (`chunk_size=500`, `overlap=50`): transcripts have no structural markers — token control gives predictable, LLM-ready chunks

## Key finding
Fixed-size chunking broke sentences in **96% of PDF chunks** — it is unsuitable for structured documents. Recursive splitting cut that to 67%. Token-based is the safest choice for production RAG pipelines regardless of content type.
