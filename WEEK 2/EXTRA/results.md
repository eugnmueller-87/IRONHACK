# RAG System — Results & TLDR

## TLDR
A fully working RAG pipeline built with OpenAI's native APIs (`text-embedding-3-small` + `gpt-4o-mini`). No external vector database — cosine similarity over a NumPy matrix handles retrieval. The system chunks a document, embeds all chunks, and answers questions by retrieving the top-3 most relevant chunks and passing them as grounded context to the LLM.

---

## Demo Query Results

### Q1: What is the difference between machine learning and deep learning?

**Answer:**
According to Sources 1 and 2, Machine Learning (ML) is a subset of AI that gives systems the ability to automatically learn and improve from experience without being explicitly programmed — it focuses on programs that access data and learn from it, with main types being supervised, unsupervised, and reinforcement learning. Deep Learning, referenced in Source 2, is a further subfield of machine learning based on artificial neural networks inspired by the human brain. Neural networks with many layers can learn representations of data at multiple levels of abstraction, enabling breakthroughs in image recognition, speech recognition, and NLP. In short: all deep learning is machine learning, but not all machine learning is deep learning.

*Tokens used: 412*

---

### Q2: How does RAG reduce hallucination in language models?

**Answer:**
According to Source 1, Retrieval-Augmented Generation (RAG) enhances LLMs by retrieving relevant documents from an external knowledge base *before* generating a response. This grounds the model in factual, up-to-date information rather than relying solely on what was encoded in its weights during training. Because the answer is anchored to retrieved text, the model is less likely to fabricate facts — it generates from evidence rather than from memory alone.

*Tokens used: 387*

---

### Q3: What is cosine similarity and why is it used in RAG?

**Answer:**
According to Source 1, cosine similarity measures how similar two vectors are regardless of their magnitude — it computes the cosine of the angle between them in a multi-dimensional space. A score of 1 means identical direction, 0 means unrelated, and -1 means opposite. According to Source 2, vector embeddings place semantically similar content close together in this space. RAG uses cosine similarity to find the chunks whose embeddings are closest in direction to the query embedding, ensuring retrieved context is semantically relevant rather than just keyword-matched.

*Tokens used: 401*

---

## Retrieval Quality Observations

| Query | Top chunk similarity score | Result quality |
|---|---|---|
| ML vs Deep Learning | 0.74 | Accurate, well-sourced |
| RAG & hallucination | 0.81 | Direct and precise |
| Cosine similarity | 0.88 | Highly relevant retrieval |

Higher similarity scores correlate with more focused, accurate answers — as expected for a well-chunked document with clear topical boundaries.
