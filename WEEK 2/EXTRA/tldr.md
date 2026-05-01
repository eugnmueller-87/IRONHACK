# TLDR

**What:** RAG pipeline built with OpenAI's native APIs — no external vector database.

**How it works:**
1. Text is split into overlapping chunks
2. Each chunk is embedded with `text-embedding-3-small`
3. Embeddings are stored as a NumPy matrix in memory
4. At query time, cosine similarity finds the top-3 most relevant chunks
5. Those chunks are passed as context to `gpt-4o-mini`, which answers citing sources

**Key design choices:**
- In-memory NumPy store → no extra dependencies, fully transparent
- `text-embedding-3-small` → cost-efficient, strong retrieval quality
- `gpt-4o-mini` → fast and cheap for generation
- System prompt forces source citation → reduces hallucination

**Result:** The system correctly answers domain questions from the document and always cites which retrieved chunk the answer came from.
