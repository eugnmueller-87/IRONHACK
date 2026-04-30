# Lab 3 — Results Report
**Lab:** Python Refactoring — Modular Design & Error Handling  
**Model:** GPT-4o-mini  
**Products processed:** 3  
**Date:** 2026-04-30

---

## What we started with

The starter code had one function that did everything at once — read the file,
validate the data, call the API, save the results. If anything went wrong,
it either crashed with a Python error you had to google, or did nothing at all
because of `except: pass` (silent failure).

Example of what "bad" looks like when the file is missing:

```
FileNotFoundError: [Errno 2] No such file or directory: 'products.json'
```

No idea which function caused it. No suggestion. Just a crash.

---

## What we built

The refactored version splits everything into 9 small functions that each do
exactly one thing. When something breaks, you get this instead:

```
ERROR in load_json_file(): FileNotFoundError
  Location: File 'products.json' not found
  Current directory: C:\...\LAB 3
  Suggestion: Check that the file path is correct and the file exists
```

Function name. What went wrong. Where to look. What to try. That's it.

---

## The run that worked

```
2026-04-30 10:58:41 - INFO - Loading JSON from 'products.json'
2026-04-30 10:58:41 - INFO - Successfully loaded 'products.json'
2026-04-30 10:58:41 - INFO - Loaded 3/3 valid products from 'products.json'
2026-04-30 10:58:41 - INFO - Processing product 1/3: Wireless Bluetooth Headphones
2026-04-30 10:58:45 - INFO - Description generated for 'Wireless Bluetooth Headphones'
2026-04-30 10:58:45 - INFO - Processing product 2/3: Smart Watch
2026-04-30 10:58:47 - INFO - Description generated for 'Smart Watch'
2026-04-30 10:58:47 - INFO - Processing product 3/3: Laptop Stand
2026-04-30 10:58:49 - INFO - Description generated for 'Laptop Stand'
2026-04-30 10:58:49 - INFO - Results saved to 'results.json'

Done! Generated descriptions for 3 product(s).
```

All 3 products loaded, validated, sent to OpenAI, and saved. No errors.

---

## The descriptions generated

### P001 — Wireless Bluetooth Headphones ($99.99)
> Experience unparalleled audio quality with our Wireless Bluetooth Headphones,
> designed for those who crave clarity and comfort. Featuring advanced Bluetooth 5.0
> technology, these headphones ensure seamless connectivity and a rich, immersive sound
> while the noise-cancelling function blocks out distractions, allowing you to fully enjoy
> your music or podcasts. With an impressive 30-hour battery life and an ergonomic fit,
> you can indulge in hours of wireless listening pleasure.

### P002 — Smart Watch ($249.99)
> Elevate your fitness journey with our state-of-the-art Smart Watch, designed to
> seamlessly integrate health and style. With real-time heart rate monitoring, built-in GPS,
> and advanced sleep tracking, you can effortlessly stay on top of your wellness goals,
> whether you're hitting the trails or winding down at home. Plus, its water-resistant design
> ensures it keeps up with your active lifestyle — all for just $249.99.

### P003 — Laptop Stand ($49.99)
> Elevate your workspace and enhance your productivity with our premium Laptop Stand,
> expertly crafted from durable aluminum for maximum stability and style. With adjustable
> height settings, this ergonomic design ensures you achieve the perfect viewing angle,
> reducing strain on your neck and eyes. Plus, built-in cable management keeps your space
> tidy and organized — upgrade your productivity for just $49.99!

---

## Error scenarios (before vs after)

### Missing file

| | Starter | Refactored |
|---|---|---|
| **Message** | `FileNotFoundError: No such file or directory` | Shows file path, current directory, suggestion |
| **Useful?** | No — you have to guess where it broke | Yes — tells you exactly what to check |

### Broken JSON syntax

| | Starter | Refactored |
|---|---|---|
| **Message** | `json.JSONDecodeError: ...` | Shows line number + column where the syntax is broken |
| **Useful?** | Somewhat | Yes — you open the file and go straight to that line |

### Invalid product data (e.g. negative price)

| | Starter | Refactored |
|---|---|---|
| **Message** | Nothing — `except: pass` swallows the error | Shows which product, which field, what's wrong |
| **Useful?** | No — product just disappears silently | Yes — you know exactly which field to fix |

---

## What the "advanced" extras added

**OpenAIWrapper class** — if the API call fails (network blip, rate limit),
it tries again automatically up to 3 times, waiting a bit longer each time
(2 seconds, then 4, then 8). So one bad API call doesn't kill the whole run.

**Logging** — every run saves a `.log` file with timestamps so you can look
back and see exactly what happened and when, even after the terminal is closed.

---

## What I learned

The biggest shift in thinking: **small functions are easier to fix than big ones.**

When something breaks in a 200-line function, you have to read all 200 lines.
When something breaks in a 10-line function with one job, you know immediately
what to look at.

The other big thing: **never swallow an error silently.** `except: pass` feels
convenient when you're writing the code. It's a nightmare when you're debugging
it two weeks later and have no idea why three products just disappeared.
