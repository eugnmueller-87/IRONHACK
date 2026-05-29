"""
Generates SpendLens Green Audit deck v2 (code-verified) as .pptx
Run: python3.12 generate_deck.py
Output: SpendLens_Green_Audit_LAB10.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Palette ──────────────────────────────────────────────────────────────────
GREEN_DARK  = RGBColor(0x1B, 0x5E, 0x20)
GREEN_MID   = RGBColor(0x2E, 0x7D, 0x32)
GREEN_LIGHT = RGBColor(0xA5, 0xD6, 0xA7)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE   = RGBColor(0xF1, 0xF8, 0xE9)
GREY        = RGBColor(0x55, 0x55, 0x55)
DARK        = RGBColor(0x1A, 0x1A, 0x1A)
AMBER       = RGBColor(0xF5, 0x7F, 0x17)
SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

def rgb(r, g, b):
    return RGBColor(r, g, b)

def add_rect(slide, left, top, width, height, fill_color):
    shape = slide.shapes.add_shape(1,
        Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape

def tb(slide, text, left, top, width, height,
       font_size=18, bold=False, color=DARK,
       align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txBox

def ml(slide, lines, left, top, width, height,
       font_size=14, color=DARK, bullet=True, title=None, title_size=16):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    first = True
    if title:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        r = p.add_run()
        r.text = title
        r.font.size = Pt(title_size)
        r.font.bold = True
        r.font.color.rgb = GREEN_MID
    for line in lines:
        p = tf.paragraphs[0] if (first and not title) else tf.add_paragraph()
        first = False
        r = p.add_run()
        r.text = ("• " if bullet else "") + line
        r.font.size = Pt(font_size)
        r.font.color.rgb = color
    return txBox

def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def footer(slide, text):
    add_rect(slide, 0, 6.9, 13.33, 0.6, GREEN_DARK)
    tb(slide, text, 0.5, 6.95, 12.3, 0.4,
       font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

def header(slide, title, color=GREEN_DARK, subtitle=None):
    add_rect(slide, 0, 0, 13.33, 0.9, color)
    tb(slide, title, 0.3, 0.05, 12.7, 0.8,
       font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

def table_header_row(slide, headers, col_x, col_w, y, row_h=0.45, color=GREEN_MID):
    add_rect(slide, 0.3, y, 12.7, row_h, color)
    for i, h in enumerate(headers):
        tb(slide, h, col_x[i], y + 0.05, col_w[i], row_h - 0.1,
           font_size=13, bold=True, color=WHITE)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H
blank = prs.slide_layouts[6]

def new_slide():
    return prs.slides.add_slide(blank)

# ─────────────────────────────────────────────────────────────────────────────
# TITLE SLIDE
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, GREEN_DARK)
add_rect(s, 0, 0, 13.33, 1.2, GREEN_MID)
tb(s, "SpendLens Carbon Story", 0.5, 0.15, 12, 1.0,
   font_size=40, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, "Green Software Retrofit Audit  ·  Path B  ·  v2 Code-Verified",
   0.5, 1.35, 12, 0.5, font_size=20, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)
tb(s, "Eugen Mueller  ·  Ironhack AI Engineering Bootcamp  ·  Week 6 LAB 10",
   0.5, 2.0, 12, 0.5, font_size=14, color=OFF_WHITE, align=PP_ALIGN.CENTER)
tb(s, "Artifact: eugnmueller-87/PROCUREMENT — SpendLens  (source code read)",
   0.5, 2.55, 12, 0.5, font_size=13, color=GREEN_LIGHT, align=PP_ALIGN.CENTER, italic=True)
tb(s, "Audience: CTO / Head of Engineering — SaaS productisation review",
   0.5, 3.1, 12, 0.5, font_size=13, color=WHITE, align=PP_ALIGN.CENTER)
add_rect(s, 0, 3.75, 13.33, 0.6, rgb(0x15, 0x4A, 0x18))
tb(s, "v2 correction: 3 of 5 v1 hotspots were already fixed in the codebase. This deck reflects what is actually true.",
   0.5, 3.8, 12.3, 0.5, font_size=13, bold=True, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)
footer(s, "Green Software Foundation Pillars: Carbon · Energy · Hardware · Measurement")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — HOOK
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Slide 1 — Hook: Why Green Software Matters Here")
tb(s, "SpendLens — AI-Powered Procurement Intelligence Platform",
   0.4, 1.1, 12, 0.5, font_size=18, bold=True, color=GREEN_DARK)
body = [
    "Category Strategy: 7 sequential Haiku calls per 'Generate Strategy' click (~40s, no caching)",
    "Icarus deep scan: 20+ parallel RSS feeds + 4 Grok clusters + batched Haiku analysis",
    "Icarus targeted query: full RSS re-fetch + 1 Sonnet call — on EVERY question in the session",
    "Weekly summary: 1 Sonnet call on demand for structured JSON extraction",
    "As multi-tenant SaaS: all of the above × N concurrent users",
]
ml(s, body, 0.4, 1.75, 12.5, 2.7, font_size=14, color=DARK)

add_rect(s, 0.4, 4.55, 12.5, 1.55, rgb(0xE8, 0xF5, 0xE9))
tb(s, "v2 correction vs. v1 audit:", 0.6, 4.62, 5, 0.4, font_size=14, bold=True, color=GREEN_DARK)
corrections = [
    "Supplier profiler: zero LLM calls (rule-based) — not a hotspot",
    "Category mapper: vendor_cache.json already skips re-uploads — not a hotspot",
    "Icarus analysis: already batches 15 articles/call with 5 parallel workers",
    "Category Strategy: already uses Haiku for all 7 frameworks",
]
ml(s, corrections, 0.6, 5.05, 12, 1.0, font_size=12, color=DARK)
footer(s, "Path B — Retrofit Audit  ·  v2 code-verified  ·  Artifact: eugnmueller-87/PROCUREMENT")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — ONE UNIT OF VALUE
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Slide 2 — One Unit of Value (R)", GREEN_MID)
add_rect(s, 1.0, 1.1, 11.3, 1.2, GREEN_DARK)
tb(s, 'R = "One complete Category Strategy package delivered per user session"',
   1.2, 1.2, 11, 0.95, font_size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, "Package includes:", 0.4, 2.55, 5, 0.4, font_size=15, bold=True, color=GREEN_DARK)
ml(s, ["Kraljic quadrant classification", "PESTEL analysis", "SWOT analysis", "Porter's Five Forces"],
   0.4, 3.0, 5.5, 1.9, font_size=14, color=DARK)
ml(s, ["TCO breakdown", "Negotiation levers", "3-year strategy recommendation", "~40s end-to-end today"],
   6.5, 3.0, 6.5, 1.9, font_size=14, color=DARK)
add_rect(s, 0.4, 5.1, 12.5, 1.2, rgb(0xE8, 0xF5, 0xE9))
tb(s, "Secondary R worth tracking:", 0.6, 5.17, 5, 0.38, font_size=13, bold=True, color=GREEN_DARK)
ml(s, [
    "One Icarus deep scan (big mode): 20+ RSS feeds + 4 Grok calls + N batched Haiku calls",
    "One Icarus targeted query: 1 Sonnet call + full live RSS re-fetch",
], 0.6, 5.57, 12, 0.65, font_size=12, color=DARK)
footer(s, "SCI framing: SCI = (E × I + M) / R  ·  R = one strategy package")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — HOTSPOTS (CODE-VERIFIED)
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Slide 3 — Hotspots: Code-Verified")
hotspots = [
    ("Strategy 7-call chain, no cache", "generate_all_frameworks() — 7 sequential Haiku calls, no TTL/freshness check", "HIGH"),
    ("Icarus query: live RSS re-fetch", "fetch_articles() called at top of every query_with_claude() unconditionally", "HIGH"),
    ("Sonnet for structured extraction", "query_with_claude + weekly_summary use claude-sonnet-4-6; Haiku handles this", "MEDIUM"),
    ("4 Grok clusters per big scan", "_fetch_grok_articles() queries all 4 clusters even for 1-category clients", "MEDIUM"),
    ("Zero telemetry", "No token logging, no latency tracking, no cost/R anywhere in codebase", "CRITICAL"),
]
cols = ["Hotspot", "Evidence in code", "Severity"]
cx = [0.3, 4.5, 11.0]; cw = [4.0, 6.3, 2.2]
table_header_row(s, cols, cx, cw, 1.05)
ry = 1.52
for idx, (name, desc, sev) in enumerate(hotspots):
    row_bg = rgb(0xE8, 0xF5, 0xE9) if idx % 2 == 0 else WHITE
    add_rect(s, 0.3, ry, 12.7, 0.52, row_bg)
    sc = rgb(0xC6, 0x28, 0x28) if sev == "CRITICAL" else (AMBER if sev == "HIGH" else GREEN_MID)
    tb(s, name, cx[0], ry+0.04, cw[0], 0.44, font_size=11, bold=True, color=GREEN_DARK)
    tb(s, desc, cx[1], ry+0.04, cw[1], 0.44, font_size=10, color=DARK)
    tb(s, sev,  cx[2], ry+0.04, cw[2], 0.44, font_size=12, bold=True, color=sc)
    ry += 0.54
add_rect(s, 0.3, ry+0.08, 12.7, 0.72, rgb(0xFF, 0xF9, 0xC4))
tb(s, "Skeptic: \"How confident are you?\"  →  High confidence on structure (read the code). Zero confidence on magnitude (no telemetry yet). Measurement plan on Slide 10.",
   0.5, ry+0.14, 12.3, 0.6, font_size=12, bold=True, color=rgb(0x7B, 0x60, 0x00))
footer(s, "Pillars: Energy (redundant calls) · Hardware (no batching scope) · Measurement (zero telemetry)")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — ASSUMPTIONS
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Slide 4 — Assumptions: What We Still Don't Know")
assumptions = [
    ("API Region", "Anthropic/xAI route inference to their own infra. Region undisclosed. Grid intensity varies 3–10× between US-East and EU-West."),
    ("Token counts", "Strategy prompts include full spend data context. Input tokens not instrumented — estimated 2,000–5,000/call, could be 2× higher."),
    ("Query frequency", "Unknown how often users trigger query_with_claude vs. the cached signal feed. If 5+ questions/session, live-fetch hotspot is significant."),
    ("Grok scan frequency", "Big-scan mode ~$0.13/run including Grok. Unknown if users run daily or weekly. Daily × multi-tenant = material API cost."),
    ("Multi-tenant concurrency", "Strategy generation is synchronous. No connection pooling or rate-limit handling visible. N concurrent users = N×7 queued calls."),
]
y = 1.05
for i, (label, text) in enumerate(assumptions):
    row_bg = rgb(0xE8, 0xF5, 0xE9) if i % 2 == 0 else WHITE
    add_rect(s, 0.3, y, 12.7, 0.82, row_bg)
    tb(s, f"{i+1}. {label}", 0.5, y+0.04, 3.0, 0.35, font_size=13, bold=True, color=GREEN_DARK)
    tb(s, text, 3.7, y+0.04, 9.1, 0.72, font_size=12, color=DARK, wrap=True)
    y += 0.86
add_rect(s, 0.3, y+0.05, 12.7, 0.5, rgb(0xE3, 0xF2, 0xFD))
tb(s, "Validate first: add @track_call logging — token count per call. 1 day of work. Zero functional change.",
   0.5, y+0.12, 12.3, 0.38, font_size=13, bold=True, color=rgb(0x0D, 0x47, 0xA1))
footer(s, "Honesty: structure is verified; magnitude is guessed. Measurement plan on Slide 10.")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — PILLARS MAP
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Slide 5 — GSF Pillars Map", GREEN_MID)
pillars = [
    ("CARBON", GREEN_DARK,
     ["Unknown inference region → unknown grid intensity",
      "Cannot publish SCI score until I disclosed",
      "No region config in codebase"],
     0.3, 1.05),
    ("ENERGY", GREEN_MID,
     ["7 sequential Haiku calls/R — no cache",
      "Icarus query re-fetches RSS every call",
      "Sonnet where Haiku suffices (query/weekly)"],
     0.3, 3.65),
    ("HARDWARE", rgb(0x1B, 0x5E, 0x20),
     ["Session I/O: 20+ HTTP fetches per question",
      "4 Grok clusters called regardless of scope",
      "No demand-shaping or off-peak scheduling"],
     6.8, 1.05),
    ("MEASUREMENT", rgb(0x33, 0x69, 0x1E),
     ["Zero telemetry today (tokens, latency, cost)",
      "No SCI proxy metric defined",
      "Blocks all other pillar improvements"],
     6.8, 3.65),
]
for (title, color, points, lft, tp) in pillars:
    add_rect(s, lft, tp, 6.2, 2.35, color)
    tb(s, title, lft+0.15, tp+0.1, 5.9, 0.5, font_size=20, bold=True, color=WHITE)
    for j, pt in enumerate(points):
        tb(s, "▸  " + pt, lft+0.2, tp+0.65+j*0.52, 5.8, 0.48, font_size=13, color=WHITE)
footer(s, "Priority: Measurement → Energy → Hardware → Carbon (requires infra control)")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — SOLUTION 1: STRATEGY CACHE
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Solution 1 — Strategy Result Cache")
add_rect(s, 0.3, 1.05, 12.7, 0.6, rgb(0xC6, 0x28, 0x28))
tb(s, "PROBLEM: generate_all_frameworks() runs 7 Haiku calls on every click — even when spend data and category are unchanged",
   0.5, 1.12, 12.3, 0.5, font_size=13, bold=True, color=WHITE)
# Three boxes left
for label, bg_c, text, tp in [
    ("CHANGE", GREEN_MID,
     "Hash-based cache: key = (client_name + category + spend_data_hash)\nCache full strategy dict in SQLite, TTL 7 days\nload_strategy() already exists — add freshness gate\nCache hit → skip all 7 Haiku calls, return in <100ms",
     1.8),
    ("BUSINESS OUTCOME", GREEN_DARK,
     "60–80% call reduction for returning users\nLatency: ~40s → <100ms on cache hit\nDirect Claude API cost reduction proportional to repeat rate",
     3.75),
]:
    add_rect(s, 0.3, tp, 7.5, 1.7, bg_c)
    tb(s, label, 0.5, tp+0.08, 7.2, 0.38, font_size=13, bold=True, color=GREEN_LIGHT)
    tb(s, text, 0.5, tp+0.5, 7.2, 1.15, font_size=12, color=WHITE, wrap=True)
# Right column
add_rect(s, 8.15, 1.8, 4.85, 1.2, rgb(0xE8, 0xF5, 0xE9))
tb(s, "Pillars", 8.35, 1.87, 4.4, 0.35, font_size=13, bold=True, color=GREEN_DARK)
tb(s, "Energy  ·  Carbon", 8.35, 2.22, 4.4, 0.6, font_size=18, bold=True, color=GREEN_DARK)
add_rect(s, 8.15, 3.15, 4.85, 1.2, rgb(0xF1, 0xF8, 0xE9))
tb(s, "GSF Pattern", 8.35, 3.22, 4.4, 0.35, font_size=13, bold=True, color=GREEN_DARK)
tb(s, "Static Assets — serve pre-computed results instead of recomputing on every request",
   8.35, 3.6, 4.4, 0.7, font_size=12, color=DARK)
add_rect(s, 8.15, 4.5, 4.85, 1.0, rgb(0xFF, 0xF9, 0xC4))
tb(s, "Tradeoff", 8.35, 4.57, 4.4, 0.35, font_size=13, bold=True, color=rgb(0x7B, 0x60, 0x00))
tb(s, "Cache goes stale if market conditions change → 7-day TTL + manual 'Refresh Strategy' button",
   8.35, 4.95, 4.4, 0.5, font_size=12, color=DARK)
footer(s, "Pillar: Energy · Carbon  |  Pattern: Static Assets")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — SOLUTION 2: HAIKU FOR QUERY/WEEKLY
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Solution 2 — Haiku for Icarus Query & Weekly Summary", GREEN_MID)
add_rect(s, 0.3, 1.05, 12.7, 0.6, rgb(0xC6, 0x28, 0x28))
tb(s, "PROBLEM: query_with_claude and weekly_summary use claude-sonnet-4-6 for structured JSON extraction — Haiku's strongest use case",
   0.5, 1.12, 12.3, 0.5, font_size=13, bold=True, color=WHITE)
add_rect(s, 0.3, 1.8, 5.9, 3.0, GREEN_DARK)
tb(s, "KEEP Sonnet (if needed)", 0.5, 1.87, 5.5, 0.42, font_size=14, bold=True, color=GREEN_LIGHT)
ml(s, [
    "generate_rfp_brief() — complex multi-doc reasoning",
    "(currently the ONLY candidate — evaluate first)",
    "Open-ended synthesis where output quality is critical",
    "Re-evaluate after quality eval results",
], 0.5, 2.35, 5.5, 2.3, font_size=13, color=WHITE)
add_rect(s, 6.7, 1.8, 6.3, 3.0, GREEN_MID)
tb(s, "MOVE TO Haiku", 6.9, 1.87, 5.9, 0.42, font_size=14, bold=True, color=WHITE)
ml(s, [
    "query_with_claude() — structured JSON, fixed schema",
    "weekly_summary() — structured JSON, fixed schema",
    "Both already return defined JSON shapes",
    "Two-line code change: model= parameter only",
], 6.9, 2.35, 5.9, 2.3, font_size=13, color=WHITE)
add_rect(s, 0.3, 4.95, 12.7, 0.68, rgb(0xE8, 0xF5, 0xE9))
tb(s, "Business outcome: Haiku ~15× cheaper per token. Every Icarus query and weekly summary costs ~15× less with zero schema change.",
   0.5, 5.02, 9.0, 0.55, font_size=13, bold=True, color=GREEN_DARK)
tb(s, "Energy · Carbon · Hardware", 10.0, 5.02, 3.0, 0.55, font_size=14, bold=True, color=GREEN_DARK)
add_rect(s, 0.3, 5.77, 12.7, 0.6, rgb(0xFF, 0xF9, 0xC4))
tb(s, "Caveat: Never blind downgrade. Run 5-sample quality eval on real queries before shipping. Keep Sonnet for generate_rfp_brief if needed.",
   0.5, 5.83, 12.3, 0.5, font_size=12, bold=True, color=rgb(0x7B, 0x60, 0x00))
footer(s, "Pillar: Energy · Carbon · Hardware  |  Pattern: Optimize AI Model")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — SOLUTION 3: SESSION ARTICLE CACHE
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Solution 3 — Session-Scoped Article Cache (Icarus)")
add_rect(s, 0.3, 1.05, 12.7, 0.6, rgb(0xC6, 0x28, 0x28))
tb(s, "PROBLEM: fetch_articles() is called at the top of every query_with_claude() — re-fetching 20+ RSS feeds per question in a session",
   0.5, 1.12, 12.3, 0.5, font_size=13, bold=True, color=WHITE)
add_rect(s, 0.3, 1.8, 5.9, 3.0, rgb(0xFF, 0xCC, 0xCC))
tb(s, "BEFORE (5 questions/session)", 0.5, 1.87, 5.5, 0.4, font_size=13, bold=True, color=rgb(0xC6, 0x28, 0x28))
tb(s, "for each question:\n    fetch_articles()  # 20+ HTTP calls\n    call_sonnet()\n\n→ 5 × 20+ = 100+ HTTP requests\n→ 3–5s RSS wait per question\n→ Same articles fetched 5×",
   0.5, 2.35, 5.5, 2.3, font_size=12, color=DARK)
add_rect(s, 6.7, 1.8, 6.3, 3.0, rgb(0xC8, 0xE6, 0xC9))
tb(s, "AFTER (5 questions/session)", 6.9, 1.87, 5.9, 0.4, font_size=13, bold=True, color=GREEN_DARK)
tb(s, "# Module-level cache, 15-min TTL\nfor each question:\n    articles = _get_or_fetch(client)  # 20+ HTTP only on first\n    call_haiku()\n\n→ 20+ HTTP requests total\n→ <50ms cache hit on questions 2–5",
   6.9, 2.35, 5.9, 2.3, font_size=12, color=DARK)
tb(s, "→", 6.3, 3.1, 0.8, 0.5, font_size=36, bold=True, color=GREEN_MID, align=PP_ALIGN.CENTER)
add_rect(s, 0.3, 4.95, 12.7, 0.68, rgb(0xE8, 0xF5, 0xE9))
tb(s, "Business outcome: ~80% fewer RSS HTTP requests for multi-question sessions. Follow-up questions respond in <50ms instead of 3–5s wait.",
   0.5, 5.02, 9.5, 0.55, font_size=13, bold=True, color=GREEN_DARK)
tb(s, "Energy · Hardware", 10.5, 5.02, 2.5, 0.55, font_size=14, bold=True, color=GREEN_DARK)
footer(s, "Pillar: Energy · Hardware  |  Pattern: Demand Shaping — avoid redundant network I/O")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — SOLUTION 4: INSTRUMENTATION
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Solution 4 — Instrumentation Layer (Measurement First)", GREEN_MID)
add_rect(s, 0.3, 1.05, 12.7, 0.6, rgb(0xC6, 0x28, 0x28))
tb(s, "PROBLEM: Zero telemetry in codebase. Cannot prove any improvement. Cannot make an honest green claim.",
   0.5, 1.12, 12.3, 0.5, font_size=14, bold=True, color=WHITE)
add_rect(s, 0.3, 1.8, 7.5, 3.3, rgb(0xE8, 0xF5, 0xE9))
tb(s, "@track_call decorator — 1 day of work", 0.5, 1.87, 7.2, 0.42, font_size=14, bold=True, color=GREEN_DARK)
code = ("def track_call(purpose: str):\n"
        "    def decorator(fn):\n"
        "        def wrapper(*args, **kwargs):\n"
        "            t0 = time.perf_counter()\n"
        "            resp = fn(*args, **kwargs)\n"
        "            ms = int((time.perf_counter() - t0) * 1000)\n"
        "            _log(purpose, resp.usage.input_tokens,\n"
        "                 resp.usage.output_tokens, ms, resp.model)\n"
        "            return resp\n"
        "        return wrapper\n"
        "    return decorator\n\n"
        "# Writes to: SQLite llm_telemetry table")
tb(s, code, 0.5, 2.35, 7.2, 2.65, font_size=10, color=DARK)
add_rect(s, 8.2, 1.8, 4.8, 1.4, GREEN_DARK)
tb(s, "Pillar", 8.4, 1.87, 4.4, 0.35, font_size=13, bold=True, color=GREEN_LIGHT)
tb(s, "MEASUREMENT", 8.4, 2.22, 4.4, 0.65, font_size=22, bold=True, color=WHITE)
add_rect(s, 8.2, 3.35, 4.8, 1.75, rgb(0xF1, 0xF8, 0xE9))
tb(s, "Why this is first:", 8.4, 3.42, 4.4, 0.35, font_size=13, bold=True, color=GREEN_DARK)
ml(s, [
    "Unlocks every other improvement",
    "Gives CTO cost-per-session for investors",
    "Required before any honest green claim",
    "1 day of work, zero functional change",
], 8.4, 3.82, 4.4, 1.2, font_size=12, color=DARK)
add_rect(s, 0.3, 5.25, 12.7, 1.1, GREEN_DARK)
tb(s, "/metrics Panel tab shows:", 0.5, 5.32, 4, 0.38, font_size=13, bold=True, color=GREEN_LIGHT)
metrics = ["Calls per R (session)", "Est. cost per R ($)", "Token trend 30d", "Cache hit rate"]
for i, m in enumerate(metrics):
    x = 0.5 + (i % 2) * 6.4; y = 5.72 + (i // 2) * 0.42
    tb(s, "▸ " + m, x, y, 6.2, 0.38, font_size=12, color=WHITE)
footer(s, "Pillar: Measurement  |  Pattern: Measure Application Energy Consumption")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — MEASUREMENT PLAN
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Slide 10 — Measurement Plan (2-Week Sprint)")
metrics_rows = [
    ("Tokens per strategy R", "@track_call → SQLite llm_telemetry", "Baseline wk1; track change"),
    ("API calls per strategy R", "Counter in telemetry", "<5 after cache (from 7 today)"),
    ("Strategy cache hit rate", "Hit/miss flag in telemetry", ">40% within 2 weeks"),
    ("Latency per strategy R", "Start/end timestamps", "<30s P95 (from ~40s today)"),
    ("Cost per strategy R ($)", "tokens × published pricing", "-30% within 4 weeks"),
    ("RSS fetches per session", "HTTP counter in _fetch_feed", "<20/session (from 20+/question)"),
]
cx = [0.3, 4.3, 9.0]; cw = [3.8, 4.5, 4.2]
table_header_row(s, ["Metric", "How to collect", "Success threshold"], cx, cw, 1.05)
ry = 1.52
for idx, (m, how, thresh) in enumerate(metrics_rows):
    row_bg = rgb(0xE8, 0xF5, 0xE9) if idx % 2 == 0 else WHITE
    add_rect(s, 0.3, ry, 12.7, 0.48, row_bg)
    tb(s, m,     cx[0], ry+0.04, cw[0], 0.4, font_size=11, bold=True, color=GREEN_DARK)
    tb(s, how,   cx[1], ry+0.04, cw[1], 0.4, font_size=10, color=DARK)
    tb(s, thresh,cx[2], ry+0.04, cw[2], 0.4, font_size=10, bold=True, color=GREEN_MID)
    ry += 0.5
add_rect(s, 0.3, ry+0.08, 12.7, 0.85, rgb(0xE8, 0xF5, 0xE9))
tb(s, "Success:",   0.5, ry+0.15, 1.5, 0.35, font_size=13, bold=True, color=GREEN_DARK)
tb(s, "Cache hit rate >40% AND cost/R trending down after 2 weeks = first honest, measurement-backed green claim.",
   2.1, ry+0.15, 10.7, 0.65, font_size=13, color=DARK)
footer(s, "SCI = (E × I + M) / R  ·  I = grid intensity (not yet disclosed by Anthropic/xAI) — cannot publish SCI score yet")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11 — CAVEATS
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Slide 11 — Caveats & Honesty")
add_rect(s, 0.3, 1.05, 12.7, 1.85, rgb(0xC6, 0x28, 0x28))
tb(s, "What we will NOT claim:", 0.5, 1.12, 5, 0.4, font_size=14, bold=True, color=WHITE)
for i, c in enumerate([
    "\"SpendLens is carbon neutral\" — no carbon data. Greenwashing.",
    "\"Each strategy costs X gCO₂\" — Anthropic/xAI inference region not disclosed.",
    "\"We reduced carbon by Y%\" — no before/after measurement yet. Hypothesis, not result.",
    "\"Model right-sizing saved energy\" — Haiku was already in use. Cannot claim as new saving.",
]):
    tb(s, "✗  " + c, 0.5, 1.55+i*0.40, 12.3, 0.37, font_size=11, bold=True, color=WHITE)
add_rect(s, 0.3, 3.05, 5.9, 1.9, rgb(0xE8, 0xF5, 0xE9))
tb(s, "v1 audit errors — corrected", 0.5, 3.12, 5.5, 0.4, font_size=13, bold=True, color=GREEN_DARK)
tb(s, "3 of 5 v1 hotspots were already fixed. Publishing those as improvements would have been inaccurate. Reading actual code before presenting findings matters — especially in a green audit where credibility is the point.",
   0.5, 3.57, 5.5, 1.32, font_size=11, color=DARK)
add_rect(s, 6.7, 3.05, 6.3, 1.9, rgb(0xE8, 0xF5, 0xE9))
tb(s, "What we WILL validate next", 6.9, 3.12, 5.9, 0.4, font_size=13, bold=True, color=GREEN_DARK)
for i, ns in enumerate([
    "1. Add @track_call instrumentation (1 day)",
    "2. Run 2-week baseline before any optimisation",
    "3. Request region disclosure from Anthropic",
    "4. Rerun audit with real numbers",
]):
    tb(s, ns, 6.9, 3.58+i*0.35, 5.9, 0.32, font_size=12, color=DARK)
add_rect(s, 0.3, 5.1, 12.7, 0.65, GREEN_DARK)
tb(s, "Offsets vs SCI: buying carbon offsets does NOT lower SCI score. SCI measures real energy per R. Offsets are accounted separately.",
   0.5, 5.17, 12.3, 0.52, font_size=12, bold=True, color=WHITE)
footer(s, "No unverifiable claims · Offsets ≠ SCI · v1 errors corrected · Next steps defined")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12 — BEFORE/AFTER HYPOTHESIS
# ─────────────────────────────────────────────────────────────────────────────
s = new_slide()
bg(s, OFF_WHITE)
header(s, "Slide 12 — Before / After Hypothesis", GREEN_MID)
hyp_rows = [
    ("Strategy cache (TTL 7d)", "~60–80% fewer strategy chain executions for returning users", "Cache hit rate"),
    ("Haiku for query/weekly (after eval)", "~15× token cost reduction per Icarus query and summary", "Cost/R Icarus"),
    ("Session article cache (15min TTL)", "~80% fewer RSS fetches for 5-question sessions", "HTTP fetch count"),
    ("Instrumentation layer", "All metrics now trackable; baseline established", "Data completeness"),
]
cx = [0.3, 5.0, 10.0]; cw = [4.5, 4.8, 3.2]
table_header_row(s, ["Change", "Hypothesis", "Metric (1 week)"], cx, cw, 1.05, color=GREEN_DARK)
ry = 1.52
for idx, (chg, hyp, metric) in enumerate(hyp_rows):
    row_bg = rgb(0xE8, 0xF5, 0xE9) if idx % 2 == 0 else WHITE
    add_rect(s, 0.3, ry, 12.7, 0.56, row_bg)
    tb(s, chg,   cx[0], ry+0.05, cw[0], 0.46, font_size=12, bold=True, color=GREEN_DARK)
    tb(s, hyp,   cx[1], ry+0.05, cw[1], 0.46, font_size=11, color=DARK)
    tb(s, metric,cx[2], ry+0.05, cw[2], 0.46, font_size=11, bold=True, color=GREEN_MID)
    ry += 0.58
add_rect(s, 0.3, ry+0.1, 12.7, 1.1, GREEN_DARK)
tb(s, "Combined hypothesis:", 0.5, ry+0.17, 4, 0.38, font_size=13, bold=True, color=GREEN_LIGHT)
tb(s, '"If all four changes ship: cost-per-strategy-R drops 60–70%; cost-per-Icarus-query drops ~90% — within 4 weeks, no output quality degradation (5-sample eval required for Haiku migration)."',
   0.5, ry+0.57, 12.3, 0.6, font_size=13, bold=True, color=WHITE)
add_rect(s, 0.3, ry+1.3, 12.7, 0.42, rgb(0xFF, 0xF9, 0xC4))
tb(s, "Hypothesis, not claim. Actual numbers presented after 2-week measurement window.",
   0.5, ry+1.35, 12.3, 0.33, font_size=13, bold=True, color=rgb(0x7B, 0x60, 0x00))
footer(s, "Hypothesis · Measurement-gated · Quality-eval required for Haiku migration")

# ── Save ──────────────────────────────────────────────────────────────────────
out = r"c:\Users\eugnm\OneDrive\Desktop\ironhack\Week 6\LAB 10\SpendLens_Green_Audit_LAB10.pptx"
prs.save(out)
print(f"Saved: {out}")
