# Week 4 — Lab 3: n8n Node Analysis

Systematic study of n8n nodes across three class workflows: Google Sheets integration, PDF-based RAG system, and AI agent chat.

## Files

| File | Description |
|------|-------------|
| [node-reference-table.md](node-reference-table.md) | Comprehensive reference table for 20 nodes — parameters, settings, JSON input/output, and key transformations |
| [lab_summary.md](lab_summary.md) | One-paragraph summary: most useful nodes, how to pick the right node, top debugging tip |

## How to Run / Reproduce

This lab is documentation-only — no code to execute. To reproduce the analysis:

1. Open n8n (cloud or self-hosted).
2. Import the three class workflows (Google Sheets, PDF RAG, AI agent chat).
3. For each node, open its configuration panel and run the workflow to observe input/output JSON in the execution view.
4. Cross-reference node schemas with `npx --yes n8nac skills node-info <nodeName>`.

## Nodes Analyzed

20 node types documented, including: Manual Trigger, Webhook, HTTP Request, Set, Code, IF, Switch, Split In Batches, Merge, Wait, OpenAI, AI Agent, Embeddings OpenAI, Pinecone Vector Store, Document Loader, Text Splitter, Cohere Reranker, Chat Trigger, Window Buffer Memory, Google Sheets.
