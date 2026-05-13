# TLDR — Python Refactoring Lab

## What is this lab in one sentence?

You take a working-but-messy Python script that generates product descriptions
using the OpenAI API, and you break it apart into clean, focused pieces that
tell you **where** and **why** things go wrong instead of just crashing silently.

---

## The scenario

**Problem:** The product description generator works — but when something breaks,
you get a cryptic Python crash (or nothing at all).  
**Root cause:** All the logic is crammed into one giant function with `except: pass`
(silent failure) everywhere.  
**Your job:** Refactor the code into professional-grade modules with proper error handling.

---

## The product used in this lab

Three sample products processed by the script:

| ID | Name | Category | Price |
|----|------|----------|------:|
| P001 | Wireless Bluetooth Headphones | Electronics | $99.99 |
| P002 | Smart Watch | Wearables | $249.99 |
| P003 | Laptop Stand | Accessories | $49.99 |

---

## The 2 versions

| | Starter Code | Refactored Code |
|---|---|---|
| **File** | `product_generator_starter.py` | `product_generator_refactored.py` |
| **Error handling** | `except: pass` — crashes silently | Shows function name, file, line, suggestion |
| **Structure** | 1 function doing everything | 9 focused functions + 1 wrapper class |
| **Logging** | None | Timestamped log to file + console |
| **API key** | Hardcoded string | `.env` file via `python-dotenv` |

---

## The 9 helper functions

| Function | Single responsibility |
|---|---|
| `load_json_file()` | Read and parse a JSON file |
| `validate_product_data()` | Check product fields with Pydantic |
| `create_product_prompt()` | Build the OpenAI prompt string |
| `parse_api_response()` | Extract text from API response |
| `format_output()` | Shape the final result dict |
| `load_and_validate_products()` | Combine loading + validation |
| `generate_description()` | Call OpenAI for one product |
| `process_products()` | Loop through all products |
| `save_results()` | Write results to JSON file |

---

## The 4 error types handled

| Error | When it triggers | What the message shows |
|---|---|---|
| `FileNotFoundError` | JSON file doesn't exist | File path + current directory + suggestion |
| `JSONDecodeError` | JSON file has bad syntax | Line number + column + suggestion |
| `ValidationError` | Product has invalid/missing fields | Which fields, what's wrong |
| `APIError` | OpenAI call fails | Product name + status code + suggestion |

---

## What "good error handling" looks like

**Before (starter code):**
```
FileNotFoundError: [Errno 2] No such file or directory: 'products.json'
```

**After (refactored):**
```
ERROR in load_json_file(): FileNotFoundError
  Location: File 'products.json' not found
  Current directory: C:\...\LAB 3
  Suggestion: Check that the file path is correct and the file exists
```

---

## How to run it

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your OpenAI key to .env
OPENAI_API_KEY=sk-...

# 3. Run
python product_generator_refactored.py
```

---

## Key takeaway

Refactoring is not about rewriting code — it's about reorganising it so that
when something breaks, you know exactly where to look.

**Silent failures (`except: pass`) are the enemy of debugging.**
