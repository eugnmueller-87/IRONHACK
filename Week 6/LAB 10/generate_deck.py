"""
Generates SpendLens Green Audit deck as .pptx
Run: python3.12 generate_deck.py
Output: SpendLens_Green_Audit_LAB10.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import textwrap

# ── Palette ────────────────────────────────────────────────────────────────
GREEN_DARK  = RGBColor(0x1B, 0x5E, 0x20)   # deep forest green
GREEN_MID   = RGBColor(0x2E, 0x7D, 0x32)   # medium green
GREEN_LIGHT = RGBColor(0xA5, 0xD6, 0xA7)   # soft green accent
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
OFF_WHITE   = RGBColor(0xF1, 0xF8, 0xE9)
GREY        = RGBColor(0x55, 0x55, 0x55)
DARK        = RGBColor(0x1A, 0x1A, 0x1A)
AMBER       = RGBColor(0xF5, 0x7F, 0x17)
SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

def rgb(r, g, b):
    return RGBColor(r, g, b)

def add_filled_rect(slide, left, top, width, height, fill_color):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape

def add_text_box(slide, text, left, top, width, height,
                 font_size=18, bold=False, color=DARK,
                 align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
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

def add_multiline(slide, lines, left, top, width, height,
                  font_size=14, color=DARK, bullet=True, title=None, title_size=16):
    txBox = slide.shapes.add_textbox(
        Inches(left), Inches(top), Inches(width), Inches(height)
    )
    tf = txBox.text_frame
    tf.word_wrap = True
    first = True
    if title:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = title
        r.font.size = Pt(title_size)
        r.font.bold = True
        r.font.color.rgb = GREEN_MID
    for line in lines:
        p = tf.paragraphs[0] if (first and not title) else tf.add_paragraph()
        first = False
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        prefix = "• " if bullet else ""
        r.text = prefix + line
        r.font.size = Pt(font_size)
        r.font.color.rgb = color
    return txBox

def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

# ── Build presentation ──────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H
blank_layout = prs.slide_layouts[6]  # blank

def new_slide():
    return prs.slides.add_slide(blank_layout)

# ────────────────────────────────────────────────────────────────────────────
# TITLE SLIDE
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, GREEN_DARK)
add_filled_rect(s, 0, 0, 13.33, 1.2, GREEN_MID)
add_text_box(s, "SpendLens Carbon Story", 0.5, 0.15, 12, 1,
             font_size=40, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_text_box(s, "Green Software Retrofit Audit  |  Path B", 0.5, 1.3, 12, 0.6,
             font_size=22, color=GREEN_LIGHT, align=PP_ALIGN.CENTER, bold=False)
add_text_box(s, "Eugen Mueller  ·  Ironhack AI Engineering Bootcamp  ·  Week 6 LAB 10",
             0.5, 2.0, 12, 0.5, font_size=14, color=OFF_WHITE, align=PP_ALIGN.CENTER)
add_text_box(s, "Artifact: eugnmueller-87/PROCUREMENT — SpendLens",
             0.5, 2.5, 12, 0.5, font_size=13, color=GREEN_LIGHT, align=PP_ALIGN.CENTER, italic=True)
add_text_box(s, "Audience: CTO / Head of Engineering — SaaS productisation review",
             0.5, 3.1, 12, 0.5, font_size=13, color=WHITE, align=PP_ALIGN.CENTER)
# Bottom bar
add_filled_rect(s, 0, 6.8, 13.33, 0.7, GREEN_MID)
add_text_box(s, "Green Software Foundation Pillars: Carbon · Energy · Hardware · Measurement",
             0.5, 6.85, 12, 0.5, font_size=12, color=WHITE, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — HOOK
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_DARK)
add_text_box(s, "Slide 1 — Hook", 0.3, 0.08, 5, 0.7,
             font_size=13, color=GREEN_LIGHT, bold=False)
add_text_box(s, "Why Green Software Matters Here", 0.3, 0.05, 12, 0.8,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_text_box(s, "SpendLens — AI-Powered Procurement Intelligence Platform",
             0.4, 1.1, 12, 0.5, font_size=18, bold=True, color=GREEN_DARK)

body = [
    "Runs 5–8 sequential LLM API calls per 'Generate Strategy' click",
    "Parallel RSS fetch across 10+ feeds + Grok search + Claude synthesis per market brief",
    "One strategy generation ≈ same API cost as ~30 simple chat turns",
    "At prototype scale: tolerable.  At multi-tenant SaaS: compute cost scales linearly with users",
]
add_multiline(s, body, 0.4, 1.75, 12.5, 2.8, font_size=15, color=DARK)

add_filled_rect(s, 0.4, 4.6, 12.5, 1.5, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "Business Risk Tiers:", 0.6, 4.65, 4, 0.4,
             font_size=14, bold=True, color=GREEN_DARK)
risks = ["Cost overrun — API spend scales with users before revenue does",
         "Latency regression — slow strategy gen → user churn",
         "Brand risk — sustainability claims without measurement = greenwashing"]
add_multiline(s, risks, 0.6, 5.05, 12, 1.0, font_size=13, color=DARK)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Path B — Retrofit Audit of existing artifact", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — ONE UNIT OF VALUE
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_MID)
add_text_box(s, "Slide 2 — One Unit of Value (R)", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_filled_rect(s, 1.0, 1.1, 11.3, 1.3, GREEN_DARK)
add_text_box(s, 'R = "One complete Category Strategy package delivered per user session"',
             1.2, 1.2, 11, 1.0, font_size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_text_box(s, "That package includes:", 0.4, 2.65, 5, 0.4,
             font_size=15, bold=True, color=GREEN_DARK)
items_l = ["Kraljic quadrant classification", "PESTEL analysis", "SWOT analysis", "Porter's Five Forces"]
items_r = ["TCO breakdown", "Negotiation levers narrative", "3-year roadmap", "10-slide HTML deck export"]
add_multiline(s, items_l, 0.4, 3.1, 5.5, 2.0, font_size=14, color=DARK)
add_multiline(s, items_r, 6.5, 3.1, 6.5, 2.0, font_size=14, color=DARK)

add_filled_rect(s, 0.4, 5.2, 12.5, 1.2, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "Why R matters:",
             0.6, 5.25, 4, 0.4, font_size=14, bold=True, color=GREEN_DARK)
add_text_box(s, "R is the billing unit. Every improvement is measured as change in resource consumption per R — not per API call.\nIf we halve calls-per-R, we halve cost and carbon exposure even as user count grows.",
             0.6, 5.65, 12, 0.7, font_size=13, color=DARK, wrap=True)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "SCI framing: SCI = (E × I + M) / R   |   R = one strategy package", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — HOTSPOTS
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_DARK)
add_text_box(s, "Slide 3 — Assessment Defense: Hotspots", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

hotspots = [
    ("Category Strategy 8-call chain", "5–8 sequential Claude calls per R — no cache, no parallelism", "HIGH"),
    ("Supplier Profiler O(n) calls", "1 Claude call per supplier row — 200 suppliers = 200 serial calls", "HIGH"),
    ("Icarus RSS + Grok + Claude", "Re-fetches same feeds on every session trigger; redundant on repeat category", "MEDIUM"),
    ("Category Mapper re-runs", "Re-classifies identical rows on re-upload of same CSV", "MEDIUM"),
    ("Zero telemetry", "Cannot measure, cannot prove improvement — blocks all other fixes", "CRITICAL"),
]
col_headers = ["Hotspot", "Description", "Severity"]
header_colors = [GREEN_MID, GREEN_MID, GREEN_MID]
row_y = 1.0
col_x = [0.3, 4.5, 10.8]
col_w = [4.0, 6.0, 2.3]

# Header row
add_filled_rect(s, 0.3, row_y, 12.7, 0.45, GREEN_MID)
for i, h in enumerate(col_headers):
    add_text_box(s, h, col_x[i], row_y + 0.05, col_w[i], 0.35,
                 font_size=13, bold=True, color=WHITE)
row_y += 0.48

for idx, (name, desc, sev) in enumerate(hotspots):
    bg = rgb(0xE8, 0xF5, 0xE9) if idx % 2 == 0 else WHITE
    add_filled_rect(s, 0.3, row_y, 12.7, 0.52, bg)
    sev_color = rgb(0xC6, 0x28, 0x28) if sev == "CRITICAL" else (AMBER if sev == "HIGH" else GREEN_MID)
    add_text_box(s, name, col_x[0], row_y + 0.04, col_w[0], 0.45, font_size=12, bold=True, color=GREEN_DARK)
    add_text_box(s, desc, col_x[1], row_y + 0.04, col_w[1], 0.45, font_size=11, color=DARK)
    add_text_box(s, sev, col_x[2], row_y + 0.04, col_w[2], 0.45, font_size=12, bold=True, color=sev_color)
    row_y += 0.54

# Skeptic challenge
add_filled_rect(s, 0.3, row_y + 0.1, 12.7, 0.85, rgb(0xFF, 0xF9, 0xC4))
add_text_box(s, "Skeptical stakeholder: \"How do you know these are the real hotspots?\"",
             0.5, row_y + 0.14, 12, 0.35, font_size=13, bold=True, color=rgb(0x7B, 0x60, 0x00))
add_text_box(s, "Honest answer: These are structural inferences from code review — not instrumented data. Slide 10 defines the measurement plan to validate or overturn them.",
             0.5, row_y + 0.50, 12, 0.4, font_size=12, color=DARK, italic=True)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Pillars: Energy (redundant calls) · Hardware (unbatched) · Measurement (zero telemetry)", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — ASSUMPTIONS
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_DARK)
add_text_box(s, "Slide 4 — Assessment Defense: Assumptions", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

assumptions = [
    ("API Region", "Claude + Grok routed to Anthropic/xAI infra — region unknown. Grid carbon intensity varies 3–10× between US-East and EU-West."),
    ("Model Size", "All 8 strategy calls use claude-sonnet-4-5. Not tested whether Haiku produces acceptable quality on simpler subtasks."),
    ("Call Frequency", "Assumed 2–4 full strategy runs/week per power user. 8 calls × 4 runs = 32 Claude calls/week. Multi-tenant multiplies this fast."),
    ("Token Counts", "~3,000–6,000 tokens per strategy call estimated. Not instrumented. Could be 2× higher if full spend data passed as context."),
    ("Idle Compute", "Panel runs locally today — no always-on cost. SaaS deployment changes this significantly."),
]
y = 1.05
for i, (label, text) in enumerate(assumptions):
    bg = rgb(0xE8, 0xF5, 0xE9) if i % 2 == 0 else WHITE
    add_filled_rect(s, 0.3, y, 12.7, 0.82, bg)
    add_text_box(s, f"{i+1}. {label}", 0.5, y + 0.04, 3.0, 0.35, font_size=13, bold=True, color=GREEN_DARK)
    add_text_box(s, text, 3.7, y + 0.04, 9.1, 0.72, font_size=12, color=DARK, wrap=True)
    y += 0.86

add_filled_rect(s, 0.3, y + 0.05, 12.7, 0.5, rgb(0xE3, 0xF2, 0xFD))
add_text_box(s, "What we would validate first: add @track_call logging — token count per call. 1 day of work. Zero functional change.",
             0.5, y + 0.12, 12, 0.38, font_size=13, bold=True, color=rgb(0x0D, 0x47, 0xA1))

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Honesty: These are guesses — not measurements. Measurement plan on Slide 10.", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — PILLARS MAP
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_MID)
add_text_box(s, "Slide 5 — GSF Pillars Map", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

pillars = [
    ("CARBON", GREEN_DARK,
     ["Unknown inference region", "No SCI score tracked", "Cannot claim carbon reduction yet"],
     0.3, 1.05),
    ("ENERGY", GREEN_MID,
     ["8 sequential LLM calls / R — no parallelism", "Icarus re-fetches same RSS feeds", "No semantic cache layer"],
     0.3, 3.65),
    ("HARDWARE", rgb(0x1B, 0x5E, 0x20),
     ["Supplier profiler: O(n) serial calls", "Category mapper re-runs on re-upload", "No demand-shaping / off-peak scheduling"],
     6.8, 1.05),
    ("MEASUREMENT", rgb(0x33, 0x69, 0x1E),
     ["Zero telemetry today", "No cost-per-R metric", "Blocks all other pillar improvements"],
     6.8, 3.65),
]

for (title, color, points, lft, tp) in pillars:
    add_filled_rect(s, lft, tp, 6.2, 2.35, color)
    add_text_box(s, title, lft + 0.15, tp + 0.1, 5.9, 0.5,
                 font_size=20, bold=True, color=WHITE)
    for j, pt in enumerate(points):
        add_text_box(s, "▸  " + pt, lft + 0.2, tp + 0.65 + j * 0.52, 5.8, 0.48,
                     font_size=13, color=WHITE)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Priority: Measurement first → Energy (quick wins) → Hardware → Carbon (requires infra control)", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — SOLUTION 1: SEMANTIC CACHE
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_DARK)
add_text_box(s, "Solution 1 — Semantic Response Cache", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

boxes = [
    ("PROBLEM", rgb(0xC6, 0x28, 0x28), WHITE,
     "Strategy chain re-runs all 8 LLM calls even when spend data and category selection have not changed since last session.",
     0.3, 1.05, 5.8),
    ("CHANGE", GREEN_MID, WHITE,
     "Hash-based cache keyed on (category_name + spend_data_hash + model_id).\nCache strategy JSON in SQLite, TTL 7 days.\nCache hit → skip full chain, serve result in <100ms.",
     0.3, 2.75, 5.8),
    ("BUSINESS OUTCOME", rgb(0x1B, 0x5E, 0x20), WHITE,
     "60–80% reduction in API calls for repeat users.\nDirect cost reduction in Claude API spend.\nLatency: ~45s → <1s on cache hit.",
     0.3, 4.55, 5.8),
]
for (label, bg, fg, text, lft, tp, w) in boxes:
    add_filled_rect(s, lft, tp, w, 1.55, bg)
    add_text_box(s, label, lft + 0.15, tp + 0.08, w - 0.3, 0.4, font_size=13, bold=True, color=GREEN_LIGHT if fg == WHITE else WHITE)
    add_text_box(s, text, lft + 0.15, tp + 0.5, w - 0.3, 1.0, font_size=12, color=WHITE, wrap=True)

# Right column — pillars + pattern
add_filled_rect(s, 6.5, 1.05, 6.5, 1.2, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "Pillars", 6.65, 1.1, 2, 0.35, font_size=13, bold=True, color=GREEN_DARK)
add_text_box(s, "Energy  ·  Carbon", 6.65, 1.45, 6.2, 0.55, font_size=18, bold=True, color=GREEN_DARK)

add_filled_rect(s, 6.5, 2.4, 6.5, 1.2, rgb(0xF1, 0xF8, 0xE9))
add_text_box(s, "Green Software Pattern", 6.65, 2.45, 6.2, 0.4, font_size=13, bold=True, color=GREEN_DARK)
add_text_box(s, "Static Assets / Demand Shaping\nServe pre-computed results instead of recomputing on every request",
             6.65, 2.85, 6.2, 0.7, font_size=12, color=DARK)

add_filled_rect(s, 6.5, 3.75, 6.5, 1.1, rgb(0xFF, 0xF9, 0xC4))
add_text_box(s, "Tradeoff", 6.65, 3.8, 6.2, 0.35, font_size=13, bold=True, color=rgb(0x7B, 0x60, 0x00))
add_text_box(s, "Cache staleness if market conditions change → mitigated by TTL + manual 'Refresh' button",
             6.65, 4.15, 6.2, 0.65, font_size=12, color=DARK)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Pillar: Energy · Carbon  |  Pattern: Static Assets / Demand Shaping", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — SOLUTION 2: MODEL RIGHT-SIZING
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_MID)
add_text_box(s, "Solution 2 — Model Right-Sizing (Tiered Calls)", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_filled_rect(s, 0.3, 1.05, 12.7, 0.6, rgb(0xC6, 0x28, 0x28))
add_text_box(s, "PROBLEM: All 8 strategy subtasks use the same large Sonnet model — including simple formatting tasks that don't need frontier capability",
             0.5, 1.12, 12.3, 0.5, font_size=13, bold=True, color=WHITE)

# Two column model routing
add_filled_rect(s, 0.3, 1.8, 6.0, 3.3, GREEN_DARK)
add_text_box(s, "KEEP Sonnet (high-reasoning)", 0.5, 1.87, 5.7, 0.45, font_size=14, bold=True, color=GREEN_LIGHT)
sonnet_tasks = ["Kraljic quadrant classification", "Porter's competitive analysis", "Negotiation Levers narrative", "Strategic Roadmap synthesis"]
for i, t in enumerate(sonnet_tasks):
    add_text_box(s, "▸ " + t, 0.5, 2.4 + i * 0.56, 5.7, 0.5, font_size=13, color=WHITE)

add_filled_rect(s, 6.7, 1.8, 6.3, 3.3, GREEN_MID)
add_text_box(s, "DOWNGRADE to Haiku (structured output)", 6.9, 1.87, 5.9, 0.45, font_size=14, bold=True, color=WHITE)
haiku_tasks = ["PESTEL bullet expansion", "SWOT table fill", "TCO row generation", "Deck slide formatting"]
for i, t in enumerate(haiku_tasks):
    add_text_box(s, "▸ " + t, 6.9, 2.4 + i * 0.56, 5.9, 0.5, font_size=13, color=WHITE)

add_filled_rect(s, 0.3, 5.25, 12.7, 0.7, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "Business outcome: Haiku ~15× cheaper per token. 4/8 calls on Haiku → est. 40–50% cost reduction per R.",
             0.5, 5.3, 8.5, 0.55, font_size=13, bold=True, color=GREEN_DARK)
add_text_box(s, "Energy · Carbon · Hardware", 9.5, 5.3, 3.5, 0.55, font_size=16, bold=True, color=GREEN_DARK, align=PP_ALIGN.CENTER)

add_filled_rect(s, 0.3, 6.1, 12.7, 0.6, rgb(0xFF, 0xF9, 0xC4))
add_text_box(s, "Caveat: Never a blind downgrade — 5-sample quality eval required before shipping. State this on every model-size recommendation.",
             0.5, 6.15, 12.3, 0.5, font_size=12, bold=True, color=rgb(0x7B, 0x60, 0x00))

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Pillar: Energy · Carbon · Hardware  |  Pattern: Optimize AI Model", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — SOLUTION 3: BATCHED SUPPLIER PROFILER
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_DARK)
add_text_box(s, "Solution 3 — Batched Supplier Profiler", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_filled_rect(s, 0.3, 1.05, 12.7, 0.65, rgb(0xC6, 0x28, 0x28))
add_text_box(s, "PROBLEM: Supplier profiler issues 1 Claude call per supplier row → 200 suppliers = 200 sequential API calls",
             0.5, 1.12, 12.3, 0.52, font_size=14, bold=True, color=WHITE)

# Before / After
add_filled_rect(s, 0.3, 1.85, 5.9, 2.8, rgb(0xFF, 0xCC, 0xCC))
add_text_box(s, "BEFORE", 0.5, 1.9, 5.5, 0.4, font_size=14, bold=True, color=rgb(0xC6, 0x28, 0x28))
add_text_box(s, "for supplier in suppliers:\n    call_claude(supplier)   # 200 calls, serial\n\n→ 200 API calls per upload\n→ ~200s total latency\n→ O(n) cost growth",
             0.5, 2.35, 5.5, 2.2, font_size=13, color=DARK)

add_filled_rect(s, 7.1, 1.85, 5.9, 2.8, rgb(0xC8, 0xE6, 0xC9))
add_text_box(s, "AFTER", 7.3, 1.9, 5.5, 0.4, font_size=14, bold=True, color=GREEN_DARK)
add_text_box(s, "for batch in chunks(suppliers, 20):\n    call_claude(batch)   # 10-12 calls\n\n→ ~10-12 API calls per upload\n→ ~10-15s total latency\n→ ~90% call reduction",
             7.3, 2.35, 5.5, 2.2, font_size=13, color=DARK)

add_text_box(s, "→", 6.3, 3.1, 0.8, 0.5, font_size=36, bold=True, color=GREEN_MID, align=PP_ALIGN.CENTER)

add_filled_rect(s, 0.3, 4.8, 12.7, 0.7, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "Business outcome: 10× reduction in API calls. Faster completion. Significant cost reduction for large customer files.",
             0.5, 4.87, 9.0, 0.55, font_size=13, bold=True, color=GREEN_DARK)
add_text_box(s, "Energy · Hardware", 10.0, 4.87, 3.0, 0.55, font_size=16, bold=True, color=GREEN_DARK)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Pillar: Energy · Hardware  |  Pattern: Batch AI Requests", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — SOLUTION 4: INSTRUMENTATION
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_MID)
add_text_box(s, "Solution 4 — Instrumentation Layer (Measurement First)", 0.3, 0.08, 12, 0.7,
             font_size=24, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_filled_rect(s, 0.3, 1.05, 12.7, 0.6, rgb(0xC6, 0x28, 0x28))
add_text_box(s, "PROBLEM: Zero telemetry today. Cannot prove any improvement. Cannot make an honest green claim.",
             0.5, 1.12, 12.3, 0.5, font_size=14, bold=True, color=WHITE)

add_filled_rect(s, 0.3, 1.8, 7.5, 3.2, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "Implementation: @track_call decorator", 0.5, 1.87, 7.2, 0.42, font_size=14, bold=True, color=GREEN_DARK)
code = ("@track_call\n"
        "def call_claude(prompt, purpose):\n"
        "    # logs: timestamp, model, prompt_tokens,\n"
        "    # completion_tokens, latency_ms, purpose\n"
        "    ...\n\n"
        "# Writes to SQLite: llm_telemetry table\n"
        "# Adds hidden /metrics Panel tab")
add_text_box(s, code, 0.5, 2.35, 7.2, 2.5, font_size=11, color=DARK)

add_filled_rect(s, 8.2, 1.8, 4.8, 1.45, GREEN_DARK)
add_text_box(s, "Pillar", 8.4, 1.85, 4.4, 0.35, font_size=13, bold=True, color=GREEN_LIGHT)
add_text_box(s, "MEASUREMENT", 8.4, 2.2, 4.4, 0.7, font_size=22, bold=True, color=WHITE)

add_filled_rect(s, 8.2, 3.4, 4.8, 1.6, rgb(0xF1, 0xF8, 0xE9))
add_text_box(s, "Why this is first:", 8.4, 3.47, 4.4, 0.35, font_size=13, bold=True, color=GREEN_DARK)
add_text_box(s, "Unlocks every other improvement.\nGives CTO a cost-per-session number for investors.\nRequired before any green claim.",
             8.4, 3.87, 4.4, 1.05, font_size=12, color=DARK)

add_filled_rect(s, 0.3, 5.15, 12.7, 1.2, GREEN_DARK)
add_text_box(s, "What the /metrics tab would show:", 0.5, 5.22, 5, 0.4, font_size=13, bold=True, color=GREEN_LIGHT)
metrics = ["Calls per R (this session)", "Estimated cost per R (API pricing proxy)", "Token trend — last 30 days", "Cache hit rate"]
for i, m in enumerate(metrics):
    x = 0.5 + (i % 2) * 6.4
    y = 5.65 + (i // 2) * 0.4
    add_text_box(s, "▸ " + m, x, y, 6.2, 0.38, font_size=12, color=WHITE)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Pillar: Measurement  |  Pattern: Measure Application Energy Consumption", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — MEASUREMENT PLAN
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_DARK)
add_text_box(s, "Slide 10 — Measurement Plan (2-Week Sprint)", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

metrics_table = [
    ("Tokens per R", "@track_call decorator → SQLite", "Baseline week 1; -20% after cache"),
    ("API calls per R", "Counter in telemetry table", "<5 calls/R (from ~8+ today)"),
    ("Latency per R (ms)", "Start/end timestamps", "<30s P95 (from ~45s today)"),
    ("Cache hit rate", "Hit/miss flag in telemetry", ">40% within 2 weeks"),
    ("Cost per R ($)", "tokens × published API pricing", "-30% within 4 weeks"),
]
headers = ["Metric", "How to collect", "Success threshold"]
row_y = 1.05
col_x2 = [0.3, 4.3, 8.8]
col_w2 = [3.8, 4.3, 4.3]

add_filled_rect(s, 0.3, row_y, 12.7, 0.45, GREEN_MID)
for i, h in enumerate(headers):
    add_text_box(s, h, col_x2[i], row_y + 0.05, col_w2[i], 0.35,
                 font_size=13, bold=True, color=WHITE)
row_y += 0.48

for idx, (m, how, thresh) in enumerate(metrics_table):
    bg = rgb(0xE8, 0xF5, 0xE9) if idx % 2 == 0 else WHITE
    add_filled_rect(s, 0.3, row_y, 12.7, 0.5, bg)
    add_text_box(s, m, col_x2[0], row_y + 0.04, col_w2[0], 0.42, font_size=12, bold=True, color=GREEN_DARK)
    add_text_box(s, how, col_x2[1], row_y + 0.04, col_w2[1], 0.42, font_size=11, color=DARK)
    add_text_box(s, thresh, col_x2[2], row_y + 0.04, col_w2[2], 0.42, font_size=11, color=GREEN_MID, bold=True)
    row_y += 0.52

add_filled_rect(s, 0.3, row_y + 0.1, 12.7, 1.05, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "What counts as success:", 0.5, row_y + 0.17, 5, 0.38, font_size=13, bold=True, color=GREEN_DARK)
add_text_box(s, "Cache hit rate >40% AND cost/R trending down after 2 weeks = first honest, measurement-backed green claim we can make.",
             0.5, row_y + 0.55, 12, 0.55, font_size=13, color=DARK)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "SCI = (E × I + M) / R  |  E proxy = tokens × model energy est.  |  I = grid intensity (requires region disclosure)",
             0.5, 6.95, 12, 0.4, font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 11 — CAVEATS
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_DARK)
add_text_box(s, "Slide 11 — Caveats & Honesty", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_filled_rect(s, 0.3, 1.05, 12.7, 1.8, rgb(0xC6, 0x28, 0x28))
add_text_box(s, "What we will NOT claim:", 0.5, 1.12, 5, 0.4, font_size=15, bold=True, color=WHITE)
no_claims = [
    '"SpendLens is carbon neutral" — no carbon data. This would be greenwashing.',
    '"Each strategy costs X gCO₂" — Anthropic/xAI grid intensity not publicly disclosed.',
    '"We reduced carbon by Y%" — without before/after measurement, this is a hypothesis.',
]
for i, c in enumerate(no_claims):
    add_text_box(s, "✗  " + c, 0.5, 1.55 + i * 0.42, 12.3, 0.38, font_size=12, bold=True, color=WHITE)

add_filled_rect(s, 0.3, 3.0, 5.9, 2.0, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "Offsets vs SCI (lesson reminder)", 0.5, 3.07, 5.5, 0.42, font_size=13, bold=True, color=GREEN_DARK)
add_text_box(s, "Buying carbon offsets does NOT lower your SCI score. SCI measures real energy and embodied carbon per functional unit. Offsets are accounted separately and do not substitute for efficiency work.",
             0.5, 3.52, 5.5, 1.4, font_size=12, color=DARK)

add_filled_rect(s, 6.7, 3.0, 6.3, 2.0, rgb(0xE8, 0xF5, 0xE9))
add_text_box(s, "What we WILL validate next", 6.9, 3.07, 5.9, 0.42, font_size=13, bold=True, color=GREEN_DARK)
next_steps = [
    "Add @track_call instrumentation (1 day)",
    "Run 2-week baseline before any optimisation",
    "Disclose region to Anthropic support",
    "Rerun this assessment with real numbers",
]
for i, ns in enumerate(next_steps):
    add_text_box(s, f"{i+1}. {ns}", 6.9, 3.55 + i * 0.37, 5.9, 0.35, font_size=12, color=DARK)

add_filled_rect(s, 0.3, 5.15, 12.7, 0.65, GREEN_DARK)
add_text_box(s, "Stakeholder ask: Approve 1-day instrumentation sprint before any other green initiative.\nWithout measurement, all other improvements are guesses.",
             0.5, 5.2, 12.3, 0.55, font_size=13, bold=True, color=WHITE)

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "No unverifiable claims · Offsets ≠ SCI · Next steps defined", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ────────────────────────────────────────────────────────────────────────────
# SLIDE 12 — BEFORE/AFTER HYPOTHESIS
# ────────────────────────────────────────────────────────────────────────────
s = new_slide()
set_slide_bg(s, OFF_WHITE)
add_filled_rect(s, 0, 0, 13.33, 0.9, GREEN_MID)
add_text_box(s, "Slide 12 — Before / After Hypothesis", 0.3, 0.08, 12, 0.7,
             font_size=26, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

hyp_table = [
    ("Semantic cache (TTL 7d)", "~60% fewer strategy chain executions for repeat users", "Cache hit rate"),
    ("Model right-sizing (Haiku 4/8)", "~40% reduction in token cost per R", "Cost/R in telemetry"),
    ("Batched supplier profiler (20/batch)", "~90% fewer supplier API calls per upload", "Supplier calls/upload"),
    ("Instrumentation layer", "Baseline established — all metrics now trackable", "Data completeness %"),
]
hdr = ["Change", "Hypothesis", "Metric to watch (1 week)"]
row_y = 1.05
col_x3 = [0.3, 5.0, 10.0]
col_w3 = [4.5, 4.8, 3.2]

add_filled_rect(s, 0.3, row_y, 12.7, 0.45, GREEN_DARK)
for i, h in enumerate(hdr):
    add_text_box(s, h, col_x3[i], row_y + 0.05, col_w3[i], 0.35,
                 font_size=13, bold=True, color=WHITE)
row_y += 0.48

for idx, (change, hyp, metric) in enumerate(hyp_table):
    bg = rgb(0xE8, 0xF5, 0xE9) if idx % 2 == 0 else WHITE
    add_filled_rect(s, 0.3, row_y, 12.7, 0.58, bg)
    add_text_box(s, change, col_x3[0], row_y + 0.05, col_w3[0], 0.48, font_size=12, bold=True, color=GREEN_DARK)
    add_text_box(s, hyp, col_x3[1], row_y + 0.05, col_w3[1], 0.48, font_size=11, color=DARK)
    add_text_box(s, metric, col_x3[2], row_y + 0.05, col_w3[2], 0.48, font_size=11, color=GREEN_MID, bold=True)
    row_y += 0.6

add_filled_rect(s, 0.3, row_y + 0.12, 12.7, 1.1, GREEN_DARK)
add_text_box(s, "Combined hypothesis:", 0.5, row_y + 0.18, 4, 0.4, font_size=14, bold=True, color=GREEN_LIGHT)
add_text_box(s, '"If all four changes are shipped, we expect cost-per-R to drop 50–65% within 4 weeks,\nwith no measurable quality degradation (validated by 5-sample Haiku eval)."',
             0.5, row_y + 0.58, 12.3, 0.6, font_size=14, bold=True, color=WHITE)

add_filled_rect(s, 0.3, row_y + 1.35, 12.7, 0.45, rgb(0xFF, 0xF9, 0xC4))
add_text_box(s, "This is a hypothesis, not a claim. We present actual numbers after the 2-week measurement window.",
             0.5, row_y + 1.4, 12.3, 0.35, font_size=13, bold=True, color=rgb(0x7B, 0x60, 0x00))

add_filled_rect(s, 0, 6.9, 13.33, 0.6, GREEN_DARK)
add_text_box(s, "Hypothesis, not claim · Measurement-gated · Quality-eval required", 0.5, 6.95, 12, 0.4,
             font_size=11, color=GREEN_LIGHT, align=PP_ALIGN.CENTER)

# ── Save ────────────────────────────────────────────────────────────────────
out = r"c:\Users\eugnm\OneDrive\Desktop\ironhack\Week 6\LAB 10\SpendLens_Green_Audit_LAB10.pptx"
prs.save(out)
print(f"Saved: {out}")
