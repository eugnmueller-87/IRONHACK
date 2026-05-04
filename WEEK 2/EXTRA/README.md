# RAG with OpenAI Native APIs

A complete Retrieval-Augmented Generation pipeline using OpenAI's embedding and chat completion APIs — no external vector database required.

## Files

| File | Purpose |
|---|---|
| `rag_openai_native.py` | Full RAG pipeline: chunking → embeddings → vector search → generation |
| `lab_summary.md` | Design decisions (one paragraph, as required) |
| `.env` | Your OpenAI API key (create this yourself, not committed) |

## Setup

```bash
pip install openai numpy python-dotenv
```

Create a `.env` file in this folder:

```
OPENAI_API_KEY=sk-...
```

## Run

```bash
python rag_openai_native.py
```

The script will chunk the built-in sample document, embed all chunks, then answer three demo questions with source citations.

## How it works

1. **Chunk** — splits the document into overlapping word-count windows
2. **Embed** — calls `text-embedding-3-small` in batches
3. **Store** — keeps embeddings as a NumPy float matrix in memory
4. **Retrieve** — cosine similarity between query embedding and all chunk embeddings
5. **Generate** — top-k chunks are passed as context to `gpt-4o-mini`
