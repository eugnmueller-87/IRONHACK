import os
import sys
import random
from dotenv import load_dotenv

# Fix encoding so special chars print correctly on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_openai import ChatOpenAI
from langchain.tools import tool          # @tool turns a plain function into an agent tool
from langchain.agents import create_agent # builds the ReAct agent graph (replaced AgentExecutor in v1.2)
from typing import List, Dict

# Load OPENAI_API_KEY from the .env file in this directory
load_dotenv()

# The LLM is the AI "brain" — all agent reasoning flows through here.
# temperature=0.7 → moderately creative (0 = deterministic, 1 = very random)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


# ─────────────────────────────────────────────
# STEP 2: Creative Tools
#
# Each function below is decorated with @tool.
# That decoration does two things:
#   1. Wraps the function so LangChain can call it
#   2. Exposes the docstring to the LLM so it knows when to use the tool
# ─────────────────────────────────────────────

@tool
def consult_demogorgon(complaint: str) -> str:
    """Get the Demogorgon's perspective on a complaint about the Upside Down.

    The Demogorgon is a creature from the Upside Down. It might have insights
    about interdimensional inconsistencies, but its perspective is... unique.

    Args:
        complaint: The complaint about the Upside Down

    Returns:
        The Demogorgon's perspective (creative and possibly chaotic)
    """
    # Three possible responses — one is chosen at random each call
    responses = [
        f"The Demogorgon tilts its head. It seems confused by '{complaint}'. Perhaps the issue is that you're thinking in three dimensions?",
        f"The Demogorgon makes a sound that might be agreement. It suggests that the problem might be temporal - things work differently in the Upside Down's time.",
        f"The Demogorgon appears to be eating something. It doesn't seem to understand the concept of '{complaint}' - maybe consistency isn't a priority there?",
    ]
    return random.choice(responses)


@tool
def check_hawkins_records(query: str) -> str:
    """Search Hawkins historical records for information.

    Hawkins, Indiana has a long history of strange occurrences. These records
    might contain clues about patterns or explanations.

    Args:
        query: What to search for in the records

    Returns:
        Information from Hawkins historical records
    """
    # Fake database — keyword → matching record
    records = {
        "portal":      "Records show portals have opened on various dates with no clear pattern. Weather, electromagnetic activity, and unknown factors seem involved.",
        "monsters":    "Historical records indicate creatures from the Upside Down behave differently based on environmental factors, time of day, and proximity to certain individuals.",
        "psychics":    "Records show that psychic abilities vary greatly. Some individuals can move objects but not see the future, others can see visions but not move things.",
        "electricity": "Hawkins has a history of electrical anomalies. Records suggest a connection between the Upside Down and electromagnetic fields.",
    }

    # Case-insensitive keyword search
    for key, value in records.items():
        if key in query.lower():
            return value

    # Fallback when no keyword matches
    return f"Records don't contain specific information about '{query}', but they note that many unexplained events have occurred in Hawkins over the years."


@tool
def cast_interdimensional_spell(problem: str, creativity_level: str = "medium") -> str:
    """Suggest a creative interdimensional spell to fix a problem.

    Sometimes the best solution is a creative one that doesn't follow normal rules.
    This tool suggests imaginative fixes for Upside Down problems.

    Args:
        problem: The problem to solve
        creativity_level: How creative to be (low, medium, high)

    Returns:
        A creative spell or solution suggestion
    """
    # low=1 spell, medium=2, high=3
    creativity_multiplier = {"low": 1, "medium": 2, "high": 3}.get(creativity_level, 2)

    spells = [
        f"Try chanting 'Becma Becma Becma' three times while holding a Walkman. This might recalibrate the interdimensional frequencies related to: {problem}",
        f"Create a salt circle and place a compass in the center. The magnetic anomalies might help stabilize: {problem}",
        f"Play 'Running Up That Hill' backwards at the exact location of the issue. The temporal resonance could fix: {problem}",
        f"Gather three items: a lighter, a compass, and something personal. Arrange them in a triangle while thinking about: {problem}. The emotional connection might help.",
    ]

    # Pick N unique spells without repeating
    selected = random.sample(spells, min(creativity_multiplier, len(spells)))
    return "\n".join(selected)


@tool
def gather_party_wisdom(question: str) -> str:
    """Ask the D&D party (Mike, Dustin, Lucas, Will) for their collective wisdom.

    The party has solved many mysteries together. Their combined knowledge
    and different perspectives can provide insights.

    Args:
        question: The question or problem to ask the party about

    Returns:
        The party's collective wisdom and suggestions
    """
    # Same keyword-matching pattern as check_hawkins_records
    party_responses = {
        "portal":      "Mike: 'Portals are unpredictable, but they usually open near strong emotional events or electromagnetic disturbances.' Dustin: 'Also, they seem to follow some kind of pattern related to the Mind Flayer's activity.'",
        "monsters":    "Lucas: 'Demogorgons are territorial but also opportunistic.' Will: 'They can sense fear and strong emotions. Maybe that's why they act differently sometimes.'",
        "psychics":    "Mike: 'El's powers seem connected to her emotional state.' Dustin: 'And they're limited by her physical and mental energy. That's probably why she can't do everything.'",
        "electricity": "Lucas: 'The Upside Down seems to interfere with electrical systems.' Dustin: 'But it also creates strange connections. It's like a feedback loop.'",
    }

    for key, response in party_responses.items():
        if key in question.lower():
            return response

    # Generic fallback when no keyword matches
    return "The party huddles together. Mike: 'This is a tough one.' Dustin: 'We need more information.' Lucas: 'Let's think about what we know.' Will: 'Maybe we should consult other sources?'"


# All 4 tools in one list — this is what we hand to create_agent()
tools = [
    consult_demogorgon,
    check_hawkins_records,
    cast_interdimensional_spell,
    gather_party_wisdom,
]

print(f"Created {len(tools)} creative tools:")
for t in tools:
    print(f"  - {t.name}: {t.description[:60]}...")


# ─────────────────────────────────────────────
# STEP 3: Build the Agent
#
# create_agent wires the LLM + tools into a ReAct loop:
#   1. LLM reads the complaint
#   2. LLM picks a tool to call (or decides to stop)
#   3. Tool runs and returns a result
#   4. LLM reads the result and decides next step
#   5. Repeat until the LLM has enough to give a final answer
# ─────────────────────────────────────────────

# The system prompt shapes the agent's personality and rules.
# It is NOT the user's complaint — it's the background instructions.
SYSTEM_PROMPT = """You are Becma, the creative director of the Downside-Up Complaint Bureau.
Your job is to handle complaints about inconsistencies in the Normal Objects universe
(an alternate-reality version of Hawkins, Indiana).

You have access to several tools that give you information and creative solutions.
Use them freely and in any order you think is helpful. Be imaginative and entertaining
while still providing thoughtful explanations.

Guidelines:
- Use at least 2 different tools per complaint to cross-reference information
- Combine insights from multiple sources into a coherent (but fun) response
- Feel free to suggest creative, interdimensional solutions
- Keep responses entertaining but informative
- Always acknowledge the complaint before diving into solutions
"""

agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)


# ─────────────────────────────────────────────
# STEP 4: Handle Complaints
# ─────────────────────────────────────────────

# The 4 complaints we'll test with
complaints = [
    "Why do demogorgons sometimes eat people and sometimes don't?",
    "The portal opens on different days—is there a schedule?",
    "Why can some psychics see the Upside Down and others can't?",
    "Why do creatures and power lines react so strangely together?",
]


def handle_complaint(complaint: str, tracker: "ToolUsageTracker | None" = None) -> str:
    """Send one complaint to the agent and print each tool call as it happens."""
    print(f"\n{'='*60}")
    print(f"COMPLAINT: {complaint}")
    print(f"{'='*60}\n")

    # invoke() runs the full ReAct loop and returns when the agent is done
    result = agent.invoke({"messages": [("human", complaint)]})

    # Walk the message history to find tool calls (msg.type == "tool")
    tools_used = []
    for msg in result["messages"]:
        if getattr(msg, "type", "") == "tool":
            tool_name = getattr(msg, "name", "unknown")
            tools_used.append(tool_name)
            # Print a preview of what the tool returned
            print(f"  [tool: {tool_name}] -> {str(msg.content)[:120]}...")

    # Log to the tracker if one was provided
    if tracker:
        tracker.record(tools_used)

    # The last message is always the agent's final answer
    final = result["messages"][-1].content
    print(f"\nTools used: {' -> '.join(tools_used) if tools_used else 'none'}")
    return final


# ─────────────────────────────────────────────
# STEP 5: Tool Usage Tracker
# ─────────────────────────────────────────────

class ToolUsageTracker:
    """Counts how many times each tool was called across all complaints."""

    def __init__(self):
        # Initialise all counts to 0 using the global tools list
        self.usage_count: Dict[str, int] = {t.name: 0 for t in tools}
        self.tool_sequences: List[str] = []  # ordered log of every call

    def record(self, tool_names: List[str]):
        """Called after each complaint with the list of tools that were used."""
        for name in tool_names:
            if name in self.usage_count:
                self.usage_count[name] += 1
        self.tool_sequences.extend(tool_names)

    def get_statistics(self) -> Dict:
        return {
            "total_tool_calls": sum(self.usage_count.values()),
            "tool_counts": self.usage_count,
            # Tool with the highest call count — None if nothing was called
            "most_used": max(self.usage_count.items(), key=lambda x: x[1])[0]
            if any(self.usage_count.values())
            else None,
        }


# ─────────────────────────────────────────────
# MAIN: Run all complaints
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*60)
    print("WELCOME TO THE DOWNSIDE-UP COMPLAINT BUREAU")
    print("Becma's Chaos Mode — Activated")
    print("="*60 + "\n")

    tracker = ToolUsageTracker()

    for complaint in complaints:
        response = handle_complaint(complaint, tracker)
        print(f"\nFINAL RESPONSE:\n{response}\n")

    # Print usage summary
    print("\n" + "="*60)
    print("=== Tool Usage Analysis ===")
    stats = tracker.get_statistics()
    print(f"Complaints handled : {len(complaints)}")
    print(f"Total tool calls   : {stats['total_tool_calls']}")
    print(f"Tool usage counts  : {stats['tool_counts']}")
    print(f"Most used tool     : {stats['most_used']}")
    print("="*60)
