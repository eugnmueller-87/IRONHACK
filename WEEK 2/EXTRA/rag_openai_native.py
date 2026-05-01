"""
RAG pipeline using OpenAI native APIs.
No external vector database — cosine similarity over numpy arrays.
"""

import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------------------------------------------------------------------
# Sample document — replace with your own text or load from a file/PDF
# ---------------------------------------------------------------------------
SAMPLE_DOCUMENT = """
Artificial Intelligence (AI) refers to the simulation of human intelligence in machines
programmed to think and learn. The field was founded in 1956 at Dartmouth College, where
researchers believed that every aspect of learning could in principle be so precisely described
that a machine could simulate it.

Machine Learning (ML) is a subset of AI that gives systems the ability to automatically learn
and improve from experience without being explicitly programmed. ML focuses on developing
programs that can access data and use it to learn for themselves. The main types of machine
learning are supervised learning, unsupervised learning, and reinforcement learning.

Deep Learning is a subfield of machine learning based on artificial neural networks inspired
by the structure and function of the human brain. Neural networks with many layers (hence
"deep") can learn representations of data with multiple levels of abstraction, enabling
breakthroughs in image recognition, speech recognition, and natural language processing.

Natural Language Processing (NLP) is a branch of AI that deals with the interaction between
computers and humans using natural language. NLP combines computational linguistics with
statistical, machine learning, and deep learning models to process human language. Key tasks
include sentiment analysis, machine translation, text summarization, and question answering.

Large Language Models (LLMs) are deep learning models trained on vast amounts of text data.
They can generate, summarize, translate, and answer questions in natural language. Examples
include GPT-4, Claude, and Gemini. LLMs are the foundation of modern AI assistants.

Retrieval-Augmented Generation (RAG) is a technique that enhances LLMs by retrieving relevant
documents from an external knowledge base before generating a response. This grounds the model
in factual, up-to-date information and reduces hallucination. RAG combines the strengths of
retrieval systems and generative models.

Vector embeddings are numerical representations of text (or images, audio, etc.) in a
high-dimensional space. Similar pieces of content are placed closer together in this space.
Embeddings are the backbone of semantic search and RAG systems, enabling retrieval of
contextually relevant chunks rather than just keyword matches.

Cosine similarity is a metric used to measure how similar two vectors are, regardless of their
magnitude. It calculates the cosine of the angle between two vectors in a multi-dimensional
space. A cosine similarity of 1 means the vectors are identical in direction; 0 means
orthogonal (unrelated); -1 means opposite. It is widely used in information retrieval.

Prompt engineering is the practice of crafting inputs to guide an LLM toward desired outputs.
Effective prompts can dramatically change the quality and relevance of model responses.
Techniques include zero-shot prompting, few-shot prompting, chain-of-thought prompting, and
role-based system messages.

Fine-tuning is the process of taking a pre-trained model and continuing to train it on a
smaller, task-specific dataset. This adapts the model's weights to a particular domain or
style, often improving performance on that task at lower inference cost than prompting alone.
"""


# ---------------------------------------------------------------------------
# Step 1: Chunking
# ---------------------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by word count."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# Step 2: Embeddings
# ---------------------------------------------------------------------------
def get_embeddings_batch(
    texts: list[str],
    model: str = "text-embedding-3-small",
    batch_size: int = 100,
) -> list[list[float]]:
    """Generate embeddings in batches for efficiency."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(model=model, input=batch)
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)} chunks")
    return all_embeddings


# ---------------------------------------------------------------------------
# Step 3: In-memory vector store
# ---------------------------------------------------------------------------
class VectorStore:
    def __init__(self):
        self.chunks: list[str] = []
        self.embeddings: np.ndarray | None = None

    def add(self, chunks: list[str], embeddings: list[list[float]]) -> None:
        self.chunks = chunks
        self.embeddings = np.array(embeddings, dtype=np.float32)

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[dict]:
        """Return top-k chunks by cosine similarity."""
        q = np.array(query_embedding, dtype=np.float32)
        # Cosine similarity: dot product of normalized vectors
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        normed = self.embeddings / (norms + 1e-10)
        q_normed = q / (np.linalg.norm(q) + 1e-10)
        scores = normed @ q_normed
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {"chunk": self.chunks[i], "score": float(scores[i]), "index": int(i)}
            for i in top_indices
        ]


# ---------------------------------------------------------------------------
# Step 4: RAG query
# ---------------------------------------------------------------------------
def rag_query(
    question: str,
    store: VectorStore,
    top_k: int = 3,
    model: str = "gpt-4o-mini",
) -> dict:
    """Retrieve relevant chunks and generate an answer."""
    # Embed the question
    q_embedding = client.embeddings.create(
        model="text-embedding-3-small", input=question
    ).data[0].embedding

    # Retrieve
    results = store.search(q_embedding, top_k=top_k)

    # Build context with source markers
    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(f"[Source {i} | similarity: {r['score']:.3f}]\n{r['chunk']}")
    context = "\n\n".join(context_parts)

    # Generate
    system_prompt = (
        "You are a helpful assistant. Answer the user's question using ONLY the "
        "provided context. If the context does not contain enough information, say so. "
        "Always cite which source(s) you used (e.g. 'According to Source 1...')."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    answer = response.choices[0].message.content

    return {
        "question": question,
        "answer": answer,
        "sources": results,
        "tokens_used": response.usage.total_tokens,
    }


# ---------------------------------------------------------------------------
# Main — build index and run demo queries
# ---------------------------------------------------------------------------
def main():
    print("=== RAG Pipeline with OpenAI Native APIs ===\n")

    # Chunk
    print("Step 1: Chunking document...")
    chunks = chunk_text(SAMPLE_DOCUMENT, chunk_size=80, overlap=15)
    print(f"  Created {len(chunks)} chunks\n")

    # Embed
    print("Step 2: Generating embeddings...")
    embeddings = get_embeddings_batch(chunks)
    print()

    # Index
    print("Step 3: Building vector store...")
    store = VectorStore()
    store.add(chunks, embeddings)
    print(f"  Indexed {len(chunks)} chunks\n")

    # Demo queries
    questions = [
        "What is the difference between machine learning and deep learning?",
        "How does RAG reduce hallucination in language models?",
        "What is cosine similarity and why is it used in RAG?",
    ]

    print("Step 4: Running demo queries\n" + "=" * 60)
    for q in questions:
        result = rag_query(q, store)
        print(f"\nQ: {result['question']}")
        print(f"A: {result['answer']}")
        print(f"   [tokens used: {result['tokens_used']}]")
        print("-" * 60)


if __name__ == "__main__":
    main()
