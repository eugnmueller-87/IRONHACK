# LAB 3 — Refactoring Lab TODO

## Setup
- [x] ~~Create `.env` file with OpenAI API key~~
- [x] ~~Create `.gitignore` so the key never goes to GitHub~~
- [x] ~~Install dependencies (`openai`, `pydantic`, `python-dotenv`)~~
- [x] ~~Create `products.json` with 3 test products~~

---

## Step 1: Understand the problem
- [x] ~~Read the starter code (`product_generator_starter.py`)~~
- [x] ~~Identify where it fails silently (`except: pass` — does nothing when something breaks)~~
- [x] ~~Identify that it's one giant function doing 5 different jobs~~

---

## Step 2: Break it into helper functions
- [x] ~~`load_json_file()` — only loads the JSON~~
- [x] ~~`validate_product_data()` — only checks if the product data is valid~~
- [x] ~~`create_product_prompt()` — only builds the text for the API~~
- [x] ~~`parse_api_response()` — only pulls the text out of what the API sends back~~
- [x] ~~`format_output()` — only shapes the final result~~

---

## Step 3: Build the main flow from those pieces
- [x] ~~`load_and_validate_products()` — loads + validates in one step~~
- [x] ~~`generate_description()` — calls OpenAI for one product~~
- [x] ~~`process_products()` — loops through all products~~
- [x] ~~`save_results()` — writes the output file~~

---

## Step 4: Add proper error handling
- [x] ~~File not found → shows file path + suggestion~~
- [x] ~~Bad JSON syntax → shows line number + suggestion~~
- [x] ~~Invalid product data → shows which fields are wrong~~
- [x] ~~API error → shows product name + error code + suggestion~~

---

## Step 5: Add extras (advanced)
- [x] ~~`OpenAIWrapper` class with retry logic (tries up to 3 times before giving up)~~
- [x] ~~Logging — saves a timestamped `.log` file every run~~

---

## Step 6: Run and test
- [x] ~~Run with `products.json` → all 3 descriptions generated successfully~~
- [ ] Run with a missing file → screenshot the error message
- [ ] Run with `malformed.json` → screenshot the JSON error
- [ ] Run with `invalid_products.json` → screenshot the validation error

---

## Deliverables
- [x] ~~`product_generator_refactored.py` — main file~~
- [x] ~~`product_generator_starter.py` — the "before" version~~
- [x] ~~`results.json` — output from successful run~~
- [x] ~~`TLDR.md` — plain English summary~~
- [x] ~~`RESULTS_REPORT.md` — what worked, what broke, what we learned~~
- [x] ~~`lab_summary.md` — required by the lab brief~~
- [ ] Screenshots of error messages
- [ ] Push everything to GitHub
