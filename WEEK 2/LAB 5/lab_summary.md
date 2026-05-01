# Lab Summary: Chunking Strategies for Podcast Transcripts and PDF Documents

## TLDR

For **PDF documents**, Recursive Character splitting (`RecursiveCharacterTextSplitter`, chunk_size=1000, overlap=200) is the best choice because PDFs have natural structure (headers, paragraphs, sections) that the recursive separator hierarchy (`\n\n` → `\n` → `. `) respects — keeping related sentences together and avoiding mid-paragraph cuts. For **podcast transcripts**, Token-Based chunking (`TokenTextSplitter`, chunk_size=500, overlap=50) wins because transcripts lack structural formatting; token-level splitting produces consistently sized chunks that fit LLM context windows predictably, and modest overlap preserves conversational continuity across turn boundaries.

---

## Results Summary

| Strategy | PDF Chunks | Podcast Chunks | Avg Chunk Size | Boundary Quality |
|---|---|---|---|---|
| Fixed-Size (char, 1000) | ~45 | ~60 | ~950 chars | Poor — frequent mid-sentence cuts |
| Recursive Char (1000, overlap 200) | ~40 | ~55 | ~850 chars | Good — respects paragraphs/sentences |
| Token-Based (500 tokens, overlap 50) | ~50 | ~65 | ~500 tokens | Good — predictable for LLMs |
| Semantic (threshold 0.7, sample only) | ~30 | ~40 | Variable | Best semantic coherence, slowest |

## Key Trade-offs

| Strategy | Pros | Cons | Best For |
|---|---|---|---|
| Fixed-Size | Simple, fast, predictable count | Breaks sentences and context arbitrarily | Quick prototyping, uniform plain text |
| Recursive Char | Preserves paragraph/sentence structure | Slightly more complex config | Structured documents (PDFs, articles) |
| Token-Based | Accurate for LLM context limits | Requires tokenizer dependency | Any production RAG pipeline |
| Semantic | Splits on meaning, not size | Slow, needs embedding model | High-quality retrieval on complex content |

## Recommendations

**PDF Documents** — use `RecursiveCharacterTextSplitter` with chunk_size=1000 and chunk_overlap=200. PDFs reward structure-aware splitting; the recursive hierarchy avoids orphaned bullet points and keeps section context intact.

**Podcast Transcripts** — use `TokenTextSplitter` with chunk_size=500 and chunk_overlap=50. Transcripts are unstructured run-on prose, so character-level structure hints are absent; controlling token count directly gives the most reliable retrieval chunks and prevents context-window overflow at query time.
