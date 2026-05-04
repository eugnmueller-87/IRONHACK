# Lab Summary: Chunking Strategies for Podcast Transcripts and PDF Documents

## TLDR

For **PDF documents**, Recursive Character splitting (`RecursiveCharacterTextSplitter`, chunk_size=1000, overlap=200) is the best choice. The EU AI Ethics Guidelines PDF (195,243 chars) produced 258 chunks with a 66.7% mid-sentence break rate — compared to 96.3% for Fixed-Size — because the recursive separator hierarchy (`\n\n` → `\n` → `. `) respects the document's paragraph and section structure. For **podcast transcripts**, Token-Based chunking (`TokenTextSplitter`, chunk_size=500, overlap=50) wins: the real Whisper transcript (16,427 chars from a 28.8 MB audio file split into 2 segments) has no structural markers, so token-level splitting produces consistently sized chunks that map directly to LLM context limits and make embeddings comparable across chunks.

---

## Results (real documents)

| Strategy | PDF chunks | Podcast chunks | Mid-sentence breaks (PDF) | Boundary quality |
|---|---|---|---|---|
| Fixed-Size (1000, overlap 100) | 217 | 20 | 96.3% | Poor |
| Recursive Char (1000, overlap 200) | 258 | 22 | 66.7% | Good |
| Token-Based (500t, overlap 50) | 162 | 10 | — | Good (token-accurate) |
| Semantic (threshold 0.75, sample) | 32 | 32 | — | Best coherence, slowest |

## Key Trade-offs

| Strategy | Pros | Cons | Best For |
|---|---|---|---|
| Fixed-Size | Simple, fast, predictable count | Breaks sentences in 96% of chunks | Quick prototyping, uniform plain text |
| Recursive Char | Preserves paragraph/sentence structure | Slightly more complex config | Structured documents (PDFs, articles) |
| Token-Based | Accurate for LLM context limits | Requires tiktoken dependency | Any production RAG pipeline |
| Semantic | Splits on meaning | Slow, needs embedding model | High-quality retrieval on complex content |

## Recommendations

**PDF Documents** — `RecursiveCharacterTextSplitter`, chunk_size=1000, chunk_overlap=200. The recursive hierarchy avoids mid-paragraph cuts and keeps section context intact.

**Podcast Transcripts** — `TokenTextSplitter`, chunk_size=500, chunk_overlap=50. Transcripts are unstructured run-on prose; token-level splitting gives the most reliable retrieval chunks and prevents context-window overflow at query time.
