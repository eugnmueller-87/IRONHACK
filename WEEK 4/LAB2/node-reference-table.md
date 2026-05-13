# n8n Node Reference Table

> Analysis based on Workflow 2 (PDF-based RAG system) and Workflow 3 (AI agent chat), supplemented with node schema research via `n8nac skills`.

---

## How to Read This Table

- **JSON Input / JSON Output** columns show the *shape* of data flowing through the node (simplified).
- **Key Transformations** describes what the node changes, adds, or removes in the data structure.
- Parameters marked `*` are required.

---

| Node | Parameters | Settings | What It Does | JSON Input | JSON Output | Key Transformations |
|------|------------|----------|--------------|------------|-------------|---------------------|
| **Manual Trigger** | _(none)_ | _(none)_ | Starts workflow on manual button click in the editor | `{}` (no input) | `[{ json: {} }]` | Emits a single empty item to kick off the workflow |
| **Webhook** | `method*` (GET/POST/…), `path*`, `responseMode` (onReceived / lastNode) | Auth (Basic/Header), Response Code, Response Headers | Receives incoming HTTP requests and converts them to n8n items | HTTP request body/headers/query | `[{ json: { body, headers, query } }]` | HTTP request → structured n8n JSON with `body`, `headers`, `query` keys |
| **HTTP Request** | `method*` (GET/POST/…), `url*`, `authentication`, `body`, `headers`, `queryParameters` | Response Format (JSON/Text/Binary), Timeout, Redirect | Makes outbound API calls to any HTTP endpoint | `[{ json: { …any… } }]` | `[{ json: <API response body> }]` | Wraps external API response as a new `json` object; previous item data is replaced unless "Include Input" is on |
| **Set** | `assignments` (key-value pairs), `includeOtherFields` (true/false) | Assignment mode (manual / expression) | Creates or overwrites fields on the current item | `[{ json: { a: 1, b: 2 } }]` | `[{ json: { a: 1, newField: "value" } }]` | Adds/overwrites specific keys; can strip all other fields when `includeOtherFields` is false |
| **Code** | `code*` (JavaScript or Python), `mode` (runOnceForAll / runForEach) | Language (JavaScript / Python) | Runs arbitrary code against items | `[{ json: { …any… } }]` | `[{ json: { …custom shape… } }]` | Full control — can reshape, filter, merge, or generate items entirely in code |
| **IF** | `conditions` (value1, operation, value2)*, `combineConditions` (AND/OR) | _(none)_ | Splits workflow into two branches based on a condition | `[{ json: { status: "active" } }]` | Same item on output 0 (true) or output 1 (false) | No data modification — items are *routed*, not transformed; both outputs carry identical JSON |
| **Switch** | `rules` (value, operation, output)*, `mode` (rules / expression) | _(none)_ | Routes items to one of N outputs based on multiple conditions | `[{ json: { type: "pdf" } }]` | Same item on the matching output branch | Same as IF — items are routed unchanged to the correct output index |
| **Split In Batches** | `batchSize*` (number), `options.reset` | _(none)_ | Splits a large array of items into smaller chunks for sequential processing | `[{ json: item1 }, { json: item2 }, …]` | Subset of items per batch execution | Passes `batchSize` items per loop iteration; maintains internal loop counter |
| **Merge** | `mode*` (append / mergeByIndex / mergeByKey / combineBySql / waitForAll) | Options per mode (key field for mergeByKey, etc.) | Combines two or more incoming data streams into one | Branch A items + Branch B items | Single merged array of items | Shape depends on mode: append stacks, mergeByIndex zips, mergeByKey deep-merges matching records |
| **Wait** | `amount*`, `unit*` (seconds/minutes/hours/days), or `resume` (webhook / form) | _(none)_ | Pauses workflow execution for a time duration or until an external event | `[{ json: { …any… } }]` | Same items after delay | Data passes through unchanged; only adds execution latency |
| **OpenAI** | `resource*` (text/image/audio/…), `operation*` (message/complete/…), `model*`, `messages` | Response Format, Max Tokens, Temperature, Top P | Calls the OpenAI API for chat completions, embeddings, image generation, etc. | `[{ json: { prompt: "…" } }]` | `[{ json: { message: { content: "…" }, … } }]` | Replaces input with the full OpenAI API response object; prompt data is consumed, AI output is the new JSON |
| **AI Agent** | `systemMessage`, `promptType` (auto / define), `text` | Max Iterations, Return Intermediate Steps | Orchestrates an LLM with tools in a ReAct loop | `[{ json: { chatInput: "…" } }]` | `[{ json: { output: "…" } }]` | Takes user message, iterates with tools, returns final agent response under `output` key |
| **Embeddings OpenAI** | `model*` (text-embedding-ada-002 / text-embedding-3-small / …) | Dimensions (for v3 models), Strip New Lines | Generates vector embeddings for text chunks | Chunk text via AI sub-node connection | Float array (embedding vector) | Text → dense numeric vector; used as sub-node input to vector stores |
| **Pinecone Vector Store** | `pineconeIndex*`, `operation` (insert / query / delete) | Namespace, Similarity Metric | Stores and retrieves vector embeddings in Pinecone | Embedding vectors + metadata | Query: matching docs with score; Insert: confirmation | Insert mode: writes vectors to index. Query mode: returns top-K nearest neighbors with similarity scores |
| **Document Loader (Default)** | `dataPropertyName` (binary field name) | _(none)_ | Loads binary data (PDF, DOCX, etc.) into LangChain document format | `[{ binary: { data: <file> } }]` | LangChain `Document` objects via AI sub-node | Converts raw binary to structured text documents with `pageContent` and `metadata` fields |
| **Text Splitter (Recursive Character)** | `chunkSize*`, `chunkOverlap` | Separators | Splits large text into overlapping chunks for embedding | LangChain `Document` objects | Array of smaller `Document` chunks | Breaks long text at natural boundaries; overlap ensures context is not lost between chunks |
| **Cohere Reranker** | `model*` (rerank-english-v2.0 / …), `topN` | _(none)_ | Re-ranks retrieved documents by relevance to the query using Cohere API | Array of retrieved docs + query | Top-N most relevant docs, reordered by score | Reorders the document list; low-relevance docs are filtered out based on `topN` |
| **Chat Trigger** | `public` (true/false), `initialMessages`, `allowFileUploads` | Authentication, Response Mode | Exposes a public chat UI and passes messages into the workflow | User chat message via UI | `[{ json: { chatInput: "…", sessionId: "…" } }]` | HTTP chat event → `chatInput` string + `sessionId` for conversation memory |
| **Window Buffer Memory** | `sessionIdType`, `sessionKey`, `contextWindowLength` | _(none)_ | Stores recent conversation turns in memory for the AI agent | AI sub-node connection (no direct item input) | Last N message turns as context | Injects conversation history into the AI prompt context window; controlled by `contextWindowLength` |
| **Google Sheets** | `resource*` (spreadsheet / sheet), `operation*` (read / append / update / clear), `spreadsheetId*`, `range` | Value Input Option, Include Values in Response | Reads from or writes to Google Sheets via the Sheets API | `[{ json: { col1: "v", col2: "v" } }]` (write) / `{}` (read) | `[{ json: { row data as key-value } }]` | Read: sheet rows → n8n items (one item per row). Write: n8n items → sheet rows; column mapping driven by field names |

---

## Node Connection Types Reference

| Connection Type | Used By | Notes |
|-----------------|---------|-------|
| `out(0).to(in(0))` | Regular data-flow nodes | Standard item passing between nodes |
| `.uses({ ai_languageModel })` | AI Agent, Chain nodes | Attaches an LLM model sub-node |
| `.uses({ ai_memory })` | AI Agent | Attaches a memory sub-node |
| `.uses({ ai_tool: [] })` | AI Agent | Attaches one or more tool sub-nodes (array) |
| `.uses({ ai_document })` | Vector Store insert mode | Attaches document loader sub-nodes (array) |
| `.uses({ ai_embedding })` | Vector Store | Attaches an embeddings model sub-node |
| `.uses({ ai_textSplitter })` | Document Loader | Attaches a text splitter sub-node |

---

## Common Expression Patterns

```
{{ $json.fieldName }}                         — current item field
{{ $('Node Name').item.json.field }}          — field from a specific upstream node
{{ $items('Node Name')[0].json.field }}       — first item from a specific node
{{ $binary.data }}                            — binary data on current item
{{ $env.MY_ENV_VAR }}                         — environment variable
```

---

## Debugging Checklist

1. **Check the execution log** — click the node in the execution view to see actual input/output JSON
2. **Use a Set node** to snapshot the current data shape at any point in the flow
3. **Check expression syntax** — must be `{{ $json.field }}`, not `$json.field` (missing braces will silently fail)
4. **Verify binary vs. JSON data** — file nodes output to `$binary`, not `$json`
5. **AI sub-node wiring** — sub-nodes (model, memory, tools) connect via `.uses()`, not data-flow arrows
