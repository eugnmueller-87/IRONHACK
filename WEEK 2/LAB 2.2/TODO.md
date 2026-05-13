# LAB | Prompt Engineering Lab — TODO

## Setup
- [x] ~~Create `prompt_engineering_lab.ipynb`~~
- [x] ~~Set up OpenAI client~~
- [x] ~~Write helper function to run multiple API calls (`call_openai`)~~

---

## Part 1: Initial Prompts (Zero-Shot Baseline)
- [x] ~~Write `sentiment_prompt_v1` — classify customer message, test once~~
- [x] ~~Write `product_prompt_v1` — generate product description, test once~~
- [x] ~~Write `extraction_prompt_v1` — extract data from feedback, test once~~

---

## Part 2: Systematic Failure Analysis
- [ ] Run all 3 prompts **5 times**, record results
- [ ] Run all 3 prompts **10 times**, compare with 5-run results
- [ ] Run all 3 prompts **15 times**, build failure analysis table
  - [ ] Consistency % per prompt
  - [ ] Number of unique response formats
  - [ ] Specific failure patterns documented

---

## Part 3: Iteration 1 — Clearer Instructions (v2)
- [x] ~~Rewrite sentiment prompt: add explicit output format + single-word constraint~~
- [x] ~~Rewrite product description prompt: add length + style guidelines~~
- [x] ~~Rewrite extraction prompt: add structured output fields~~
- [ ] Test all v2 prompts, compare consistency with v1

---

## Part 4: Iteration 2 — Few-Shot & Chain-of-Thought (v3)
- [x] ~~Add 2–3 few-shot examples to sentiment prompt, test 15 times~~
- [x] ~~Add Chain-of-Thought reasoning to data extraction prompt, test 15 times~~
- [x] ~~Add few-shot + structured format to product description prompt, test 15 times~~
- [ ] Compare v3 consistency vs v1 (target: >80%)

---

## Part 5: Task Variations & Final Evaluation
- [x] ~~Create variations for each task type (e.g. different products, different feedback messages)~~
- [ ] Test best prompts on variations, document what needs tuning
- [ ] Run final v3 prompts 15 times each
- [ ] Write comprehensive comparison report (v1 vs v3)

---

## Deliverables
- [x] ~~`prompt_engineering_lab.ipynb` — all 3 versions per task, all test runs, failure tables~~
- [ ] Failure analysis (in notebook or separate `.md`)
- [ ] `lab_summary.md` — one paragraph: what you tried, what failed/improved, best techniques, what you'd do differently
- [ ] `README.md` — how to run the notebook, map of files
- [ ] Push everything to GitHub, submit repo URL

---

## Bonus (if time allows)
- [ ] Temperature experiment (0, 0.3, 0.7, 1.0) — document findings
- [ ] Meta-prompt: use LLM to auto-improve v1 prompt
- [ ] Multi-task prompt handling all 3 tasks
- [ ] Auto-evaluation function (format adherence, content quality, consistency)
