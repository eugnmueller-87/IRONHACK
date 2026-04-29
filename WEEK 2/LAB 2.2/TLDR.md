# TLDR — Prompt Engineering Lab

## What is this lab in one sentence?

You take a broken AI chatbot (one that gives messy, unpredictable answers) and fix it
by improving the instructions you give it — three tasks, three rounds of improvement.

---

## The scenario

**Company:** TechFlow Solutions  
**Problem:** Their customer-service chatbot gives inconsistent answers. Same question, different format every time.  
**Root cause:** The prompts (instructions) sent to the AI are too vague.  
**Your job:** Fix the prompts.

---

## The 3 tasks

| Task | What it does | Example input | Expected output |
|------|-------------|---------------|-----------------|
| **A — Sentiment** | Label a customer message | *"I love this product!"* | `Positive` |
| **B — Product Description** | Write a product blurb | *Joerges Gorilla Espresso Impianto, 1 kg, €29.99* | 3-sentence description |
| **C — Data Extraction** | Pull facts from text | *"Order #12345 arrived damaged"* | `{"order_id": "12345", ...}` |

---

## The 3 rounds (v1 → v2 → v3)

### v1 — Bare minimum (what breaks)
Give the AI as little instruction as possible. Just ask the question.

```
Classify this customer message: "I love this product!"
```

**What goes wrong:** The AI might say "Positive", or "The sentiment is positive", or
"This message expresses a positive sentiment." Three different formats — all technically correct,
but useless if you need to feed the output into code.

---

### v2 — Clear rules (big improvement)
Tell the AI exactly what format you need. Be specific about every constraint.

```
You are a sentiment classifier.
Classify as exactly one word: Positive, Negative, or Neutral.
Rules:
- Respond with only that single word
- No punctuation, no explanation

Customer message: "I love this product!"
```

**What improves:** The model stops inventing its own format. Consistency jumps from ~65% to ~95%.

---

### v3 — Show examples + walk through reasoning (near-perfect)

**For classification and generation tasks — Few-Shot examples:**  
Show the model 2–3 complete examples before asking the real question.
The model copies the pattern instead of guessing.

```
Message: "This is the worst purchase I've ever made."
Negative

Message: "It arrived on time."
Neutral

Message: "I love this product!"
```
→ The model sees the pattern and returns `Positive` every single time.

**For extraction tasks — Chain-of-Thought:**  
Make the model reason step by step before writing the final answer.

```
Step 1: Find the order ID...
Step 2: Find the date...
Step 3: Decide delivery speed...
Step 4: Write the JSON.
```
→ By thinking through each field, the model almost never produces invalid JSON.

---

## How we measure "working"

| Task | Metric | How it's calculated |
|------|--------|---------------------|
| Sentiment | **Exact-match rate** | What % of 15 runs return the exact same answer? |
| Product Desc | **Length consistency** | What % of 15 runs are within ±20% of the median word count? |
| Data Extraction | **Valid JSON rate** | What % of 15 runs return parseable JSON? |

---

## Expected results

| Task | v1 | v2 | v3 |
|------|:--:|:--:|:--:|
| Sentiment | ~65% | ~95% | ~100% |
| Product Description | ~53% | ~80% | ~93% |
| Data Extraction | ~13% | ~87% | ~100% |

**The pattern is always the same:**
- v1 → v2: the biggest jump (adding rules does most of the work)
- v2 → v3: smaller but important gain (examples lock in the last edge cases)

---

## How to run it

1. Make sure your `.env` file has `OPENAI_API_KEY=sk-...` in this folder
2. Open `prompt_engineering_lab.ipynb` in Jupyter
3. Click **Run All** (`Kernel → Restart & Run All`)
4. Wait ~2 minutes (it makes ~135 API calls total)
5. Check the final comparison table in the last code cell

---

## Key takeaways (the 3 things to remember)

1. **Always give the model a role and a format rule.** "You are X. Respond with only Y."
   This alone fixes most inconsistency problems.

2. **When rules aren't enough, show an example.**
   One worked example is worth ten rules.

3. **For complex extraction, make the model think out loud.**
   Chain-of-Thought (step 1, step 2...) dramatically reduces structured-output errors.

---

## Glossary (plain English)

| Term | What it means |
|------|--------------|
| **Prompt** | The message/instruction you send to the AI |
| **Zero-shot** | Asking the AI with no examples — just a question |
| **Few-shot** | Giving the AI 2–3 examples before asking the real question |
| **Chain-of-Thought** | Making the AI reason step by step before giving the final answer |
| **Temperature** | How random/creative the AI is. 0 = very predictable, 1 = very random |
| **Consistency** | Whether the AI gives the same format of answer every time |
| **JSON** | A structured data format: `{"key": "value"}` — easy for code to read |
| **API** | The connection to the AI service — you send a prompt, you get a response |
