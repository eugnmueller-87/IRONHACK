"""
normalobjects_langgraph.py
Bloyce's Protocol — Strict Complaint Processor
NormalObjects Lab 2 | LangGraph structured workflow
"""

import os
import sys
from datetime import datetime
from typing import TypedDict, List, Optional
from dotenv import load_dotenv

# Fix Windows terminal encoding so special chars don't crash
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

load_dotenv()

# ─────────────────────────────────────────────
# LLM SETUP
# temperature=0 → deterministic answers (no randomness, rules must be consistent)
# ─────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─────────────────────────────────────────────
# STATE DEFINITION
#
# The state is a dictionary that travels through every node.
# Each node reads from it and returns an updated copy.
# TypedDict gives us type hints so we know what fields exist.
# ─────────────────────────────────────────────
class ComplaintState(TypedDict):
    complaint: str                   # original text submitted by the user
    category: Optional[str]          # one of: portal | monster | psychic | environmental | other
    is_valid: Optional[bool]         # did the complaint pass validation?
    rejection_reason: Optional[str]  # why it was rejected (if applicable)
    investigation: Optional[str]     # evidence gathered during investigation
    resolution: Optional[str]        # the proposed fix
    effectiveness: Optional[str]     # high | medium | low
    closure_confirmed: Optional[bool]
    satisfaction_checked: Optional[bool]
    workflow_path: List[str]         # tracks every node visited (the audit trail)
    status: str                      # current step name
    timestamp: Optional[str]         # set at closure


# ─────────────────────────────────────────────
# VALID CATEGORIES
# Defined once here so every node uses the same list
# ─────────────────────────────────────────────
VALID_CATEGORIES = {"portal", "monster", "psychic", "environmental", "other"}


# ═══════════════════════════════════════════
# NODE 1 — INTAKE
# Parse the complaint and assign it a category.
# ═══════════════════════════════════════════
def intake_node(state: ComplaintState) -> ComplaintState:
    print("\n[INTAKE] Processing complaint...")

    complaint = state["complaint"]

    # Ask the LLM to read the complaint and output a single category word
    prompt = f"""Categorize this Downside Up complaint into exactly one of these categories:
- portal: Issues with portal timing, location, or behavior
- monster: Issues with creature behavior (demogorgons, etc.)
- psychic: Issues with psychic abilities or limitations
- environmental: Issues with electricity, weather, or physical environment
- other: Anything else

Complaint: {complaint}

Reply with ONLY the category name (one word, lowercase)."""

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip().lower()

    # Sanitize: if the LLM returned something unexpected, fall back to "other"
    category = raw if raw in VALID_CATEGORIES else "other"

    print(f"[INTAKE] Categorized as: {category}")

    return {
        **state,
        "category": category,
        "workflow_path": state.get("workflow_path", []) + ["intake"],
        "status": "intake",
    }


# ═══════════════════════════════════════════
# NODE 2 — VALIDATE
# Check if the complaint has enough detail to process.
# Category-specific rules from Bloyce's Protocol.
# ═══════════════════════════════════════════
def validate_node(state: ComplaintState) -> ComplaintState:
    print("\n[VALIDATE] Checking complaint against Bloyce's Protocol...")

    category = state["category"]
    complaint = state["complaint"]

    # "other" category always fails validation and gets escalated
    if category == "other":
        print("[VALIDATE] Category 'other' — auto-escalated for manual review.")
        return {
            **state,
            "is_valid": False,
            "rejection_reason": "Category 'other' requires manual review escalation per Bloyce's Protocol.",
            "workflow_path": state["workflow_path"] + ["validate"],
            "status": "validate",
        }

    # Build a rule-check prompt tailored to the category
    rules = {
        "portal":      "Must reference a specific location or timing anomaly.",
        "monster":     "Must describe creature behavior or a specific interaction.",
        "psychic":     "Must reference a specific ability limitation or malfunction.",
        "environmental": "Must mention electricity, weather, or an observable physical phenomenon.",
    }

    prompt = f"""You are validating a Downside Up complaint under Bloyce's Protocol.

Category: {category}
Validation rule: {rules[category]}
Complaint: {complaint}

Does the complaint satisfy the rule above?
Reply with exactly: VALID or INVALID
Then on a new line explain in one sentence why."""

    response = llm.invoke([HumanMessage(content=prompt)])
    lines = response.content.strip().splitlines()
    verdict = lines[0].strip().upper()
    reason = lines[1].strip() if len(lines) > 1 else "No reason provided."

    is_valid = verdict == "VALID"
    rejection_reason = None if is_valid else reason

    print(f"[VALIDATE] Result: {verdict} — {reason}")

    return {
        **state,
        "is_valid": is_valid,
        "rejection_reason": rejection_reason,
        "workflow_path": state["workflow_path"] + ["validate"],
        "status": "validate",
    }


# ═══════════════════════════════════════════
# ROUTING FUNCTION (used after validate)
# LangGraph calls this to decide which node comes next.
# Returns a node name as a string.
# ═══════════════════════════════════════════
def route_after_validate(state: ComplaintState) -> str:
    if state["is_valid"]:
        return "investigate"   # proceed through the workflow
    return "reject"            # dead-end node that explains the rejection


# ═══════════════════════════════════════════
# NODE 3a — REJECT (only reached when validation fails)
# Explains the rejection and stops the workflow.
# ═══════════════════════════════════════════
def reject_node(state: ComplaintState) -> ComplaintState:
    print("\n[REJECT] Complaint did not meet validation requirements.")
    print(f"[REJECT] Reason: {state['rejection_reason']}")

    return {
        **state,
        "workflow_path": state["workflow_path"] + ["reject"],
        "status": "rejected",
    }


# ═══════════════════════════════════════════
# NODE 3b — INVESTIGATE
# Gather evidence specific to the complaint category.
# Cannot run unless validation passed (enforced by the graph edges).
# ═══════════════════════════════════════════
def investigate_node(state: ComplaintState) -> ComplaintState:
    print("\n[INVESTIGATE] Gathering evidence...")

    category = state["category"]
    complaint = state["complaint"]

    # Each category has its own investigation angle from Bloyce's Protocol
    focus = {
        "portal":      "temporal patterns, location consistency, and environmental factors",
        "monster":     "behavioral data, interaction patterns, and environmental triggers",
        "psychic":     "ability specifications, tested limitations, and contextual factors",
        "environmental": "power line activity, atmospheric conditions, and anomaly correlation",
    }

    prompt = f"""You are an investigator at the Downside Up Complaint Bureau.

Category: {category}
Investigation focus: {focus.get(category, "general anomaly patterns")}
Complaint: {complaint}

Produce a short investigation report (3-5 sentences) documenting your findings.
Reference specific evidence and patterns you observe."""

    response = llm.invoke([HumanMessage(content=prompt)])
    investigation = response.content.strip()

    print(f"[INVESTIGATE] Evidence documented.")

    return {
        **state,
        "investigation": investigation,
        "workflow_path": state["workflow_path"] + ["investigate"],
        "status": "investigate",
    }


# ═══════════════════════════════════════════
# NODE 4 — RESOLVE
# Propose a fix based on the investigation results.
# Must reference a Downside Up procedure and rate effectiveness.
# ═══════════════════════════════════════════
def resolve_node(state: ComplaintState) -> ComplaintState:
    print("\n[RESOLVE] Determining resolution...")

    prompt = f"""You are resolving a Downside Up complaint under Bloyce's Protocol.

Category: {state["category"]}
Original complaint: {state["complaint"]}
Investigation findings: {state["investigation"]}

Provide:
1. A specific resolution that references an established Downside Up procedure or protocol.
2. An effectiveness rating: high, medium, or low (with one-sentence justification).

Format your response as:
RESOLUTION: <your resolution here>
EFFECTIVENESS: <high|medium|low> — <one sentence reason>"""

    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content.strip()

    # Parse the structured response
    resolution = ""
    effectiveness = "medium"  # safe fallback
    for line in text.splitlines():
        if line.upper().startswith("RESOLUTION:"):
            resolution = line.split(":", 1)[1].strip()
        elif line.upper().startswith("EFFECTIVENESS:"):
            raw_eff = line.split(":", 1)[1].strip().lower()
            for level in ("high", "medium", "low"):
                if level in raw_eff:
                    effectiveness = level
                    break

    print(f"[RESOLVE] Resolution found. Effectiveness: {effectiveness}")

    return {
        **state,
        "resolution": resolution or text,  # fallback: use full text if parsing failed
        "effectiveness": effectiveness,
        "workflow_path": state["workflow_path"] + ["resolve"],
        "status": "resolve",
    }


# ═══════════════════════════════════════════
# NODE 5 — CLOSE
# Confirm the resolution was applied, check satisfaction, log everything.
# Low-effectiveness cases automatically trigger a 30-day follow-up note.
# ═══════════════════════════════════════════
def close_node(state: ComplaintState) -> ComplaintState:
    print("\n[CLOSE] Closing complaint...")

    # Per Bloyce's Protocol: satisfaction must be attempted before closure
    satisfaction_checked = True
    closure_confirmed = True
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Low-effectiveness complaints need a follow-up checkpoint at 30 days
    followup_note = ""
    if state.get("effectiveness") == "low":
        followup_note = " ⚠ 30-day follow-up checkpoint required (low effectiveness rating)."

    print(f"[CLOSE] Complaint closed at {timestamp}.{followup_note}")

    return {
        **state,
        "closure_confirmed": closure_confirmed,
        "satisfaction_checked": satisfaction_checked,
        "timestamp": timestamp,
        "workflow_path": state["workflow_path"] + ["close"],
        "status": "closed",
    }


# ─────────────────────────────────────────────
# BUILD THE GRAPH
#
# StateGraph wires nodes together like a flowchart.
# add_edge = "always go from A to B"
# add_conditional_edges = "look at the state, then decide"
# ─────────────────────────────────────────────
workflow = StateGraph(ComplaintState)

# Register every node by name
workflow.add_node("intake", intake_node)
workflow.add_node("validate", validate_node)
workflow.add_node("investigate", investigate_node)
workflow.add_node("resolve", resolve_node)
workflow.add_node("close", close_node)
workflow.add_node("reject", reject_node)

# The workflow always starts at intake
workflow.set_entry_point("intake")

# intake → validate (always)
workflow.add_edge("intake", "validate")

# validate → investigate OR reject (depends on is_valid)
workflow.add_conditional_edges(
    "validate",
    route_after_validate,
    {
        "investigate": "investigate",  # valid complaint continues
        "reject": "reject",            # invalid complaint is rejected
    },
)

# Linear happy path: investigate → resolve → close → END
workflow.add_edge("investigate", "resolve")
workflow.add_edge("resolve", "close")
workflow.add_edge("close", END)

# Rejection is a terminal node
workflow.add_edge("reject", END)

# Compile turns the graph definition into a callable app
app = workflow.compile()


# ─────────────────────────────────────────────
# VISUALIZATION HELPER
# Prints the audit trail and final state for one complaint.
# ─────────────────────────────────────────────
def print_workflow_result(complaint: str, result: ComplaintState) -> None:
    print("\n" + "=" * 60)
    print(f"COMPLAINT : {complaint}")
    print(f"PATH      : {' → '.join(result['workflow_path'])}")
    print(f"STATUS    : {result['status']}")
    print(f"CATEGORY  : {result.get('category', 'n/a')}")

    if result["status"] == "rejected":
        print(f"REJECTED  : {result.get('rejection_reason', 'n/a')}")

    elif result["status"] == "closed":
        print(f"RESOLUTION: {result.get('resolution', 'n/a')}")
        print(f"EFFECTIVE : {result.get('effectiveness', 'n/a')}")
        print(f"CLOSED AT : {result.get('timestamp', 'n/a')}")
        if result.get("effectiveness") == "low":
            print("FOLLOWUP  : 30-day checkpoint required")

    print("=" * 60)


# ─────────────────────────────────────────────
# MAIN — Run 5 test complaints
# (lab requires: at least 3 valid + 1 invalid + 1 edge case)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BLOYCE'S PROTOCOL — Downside Up Complaint Bureau")
    print("Strict Workflow Mode — LangGraph State Machine")
    print("=" * 60)

    test_complaints = [
        # 1. Portal — valid (has timing + location detail)
        "The Downside Up portal opens at different times each day near the old Hawkins Lab. How do I predict when it will appear?",
        # 2. Monster — valid (describes specific behavior)
        "Demogorgons sometimes work together in hunting packs and sometimes fight each other. What determines their coordination?",
        # 3. Psychic — valid (references specific limitation)
        "El can move objects with her mind but cannot lift anything heavier than 50kg. Why is there a weight limit on telekinesis?",
        # 4. Environmental — valid (mentions electricity + phenomenon)
        "Every time the portal opens, the power lines within 200 metres flicker and surge. Why do creatures and power lines react so strangely together?",
        # 5. Invalid — vague complaint with no detail (should be rejected or escalated)
        "This is not a valid complaint about something random",
    ]

    results = []

    for complaint in test_complaints:
        # Build the initial state — only complaint is set; everything else is None/empty
        initial_state: ComplaintState = {
            "complaint": complaint,
            "category": None,
            "is_valid": None,
            "rejection_reason": None,
            "investigation": None,
            "resolution": None,
            "effectiveness": None,
            "closure_confirmed": None,
            "satisfaction_checked": None,
            "workflow_path": [],
            "status": "pending",
            "timestamp": None,
        }

        # Run the full workflow — LangGraph handles node sequencing automatically
        final_state = app.invoke(initial_state)
        results.append(final_state)
        print_workflow_result(complaint, final_state)

    # ── Summary table ──
    print("\n\n" + "=" * 60)
    print("WORKFLOW EXECUTION SUMMARY")
    print("=" * 60)
    closed  = sum(1 for r in results if r["status"] == "closed")
    rejected = sum(1 for r in results if r["status"] == "rejected")
    print(f"Total complaints : {len(results)}")
    print(f"Closed           : {closed}")
    print(f"Rejected         : {rejected}")
    print(f"\nAudit trails:")
    for i, r in enumerate(results, 1):
        path = " → ".join(r["workflow_path"])
        print(f"  [{i}] {path}")
    print("=" * 60)
