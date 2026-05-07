import os
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from typing import List, Dict

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


# ─────────────────────────────────────────────
# STEP 2: Creative Tools
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
    records = {
        "portal": "Records show portals have opened on various dates with no clear pattern. Weather, electromagnetic activity, and unknown factors seem involved.",
        "monsters": "Historical records indicate creatures from the Upside Down behave differently based on environmental factors, time of day, and proximity to certain individuals.",
        "psychics": "Records show that psychic abilities vary greatly. Some individuals can move objects but not see the future, others can see visions but not move things.",
        "electricity": "Hawkins has a history of electrical anomalies. Records suggest a connection between the Upside Down and electromagnetic fields.",
    }

    for key, value in records.items():
        if key in query.lower():
            return value

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
    creativity_multiplier = {"low": 1, "medium": 2, "high": 3}.get(creativity_level, 2)

    spells = [
        f"Try chanting 'Becma Becma Becma' three times while holding a Walkman. This might recalibrate the interdimensional frequencies related to: {problem}",
        f"Create a salt circle and place a compass in the center. The magnetic anomalies might help stabilize: {problem}",
        f"Play 'Running Up That Hill' backwards at the exact location of the issue. The temporal resonance could fix: {problem}",
        f"Gather three items: a lighter, a compass, and something personal. Arrange them in a triangle while thinking about: {problem}. The emotional connection might help.",
    ]

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
    party_responses = {
        "portal": "Mike: 'Portals are unpredictable, but they usually open near strong emotional events or electromagnetic disturbances.' Dustin: 'Also, they seem to follow some kind of pattern related to the Mind Flayer's activity.'",
        "monsters": "Lucas: 'Demogorgons are territorial but also opportunistic.' Will: 'They can sense fear and strong emotions. Maybe that's why they act differently sometimes.'",
        "psychics": "Mike: 'El's powers seem connected to her emotional state.' Dustin: 'And they're limited by her physical and mental energy. That's probably why she can't do everything.'",
        "electricity": "Lucas: 'The Upside Down seems to interfere with electrical systems.' Dustin: 'But it also creates strange connections. It's like a feedback loop.'",
    }

    for key, response in party_responses.items():
        if key in question.lower():
            return response

    return "The party huddles together. Mike: 'This is a tough one.' Dustin: 'We need more information.' Lucas: 'Let's think about what we know.' Will: 'Maybe we should consult other sources?'"


# Register tools
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
# ─────────────────────────────────────────────

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

# create_react_agent from langgraph.prebuilt is the modern replacement for
# the deprecated AgentExecutor + create_openai_tools_agent pattern.
agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)


# ─────────────────────────────────────────────
# STEP 4: Handle Complaints
# ─────────────────────────────────────────────

complaints = [
    "Why do demogorgons sometimes eat people and sometimes don't?",
    "The portal opens on different days—is there a schedule?",
    "Why can some psychics see the Upside Down and others can't?",
    "Why do creatures and power lines react so strangely together?",
]


def handle_complaint(complaint: str) -> str:
    """Handle a single complaint through the agent and print tool steps."""
    print(f"\n{'='*60}")
    print(f"COMPLAINT: {complaint}")
    print(f"{'='*60}\n")

    result = agent.invoke({"messages": [("human", complaint)]})

    # Stream the intermediate tool calls for visibility
    tools_used = []
    for msg in result["messages"]:
        role = getattr(msg, "type", type(msg).__name__)
        if role == "tool":
            tool_name = getattr(msg, "name", "unknown")
            tools_used.append(tool_name)
            print(f"  [tool: {tool_name}] -> {str(msg.content)[:120]}...")

    final = result["messages"][-1].content
    print(f"\nTools used: {' -> '.join(tools_used) if tools_used else 'none'}")
    return final


# ─────────────────────────────────────────────
# STEP 5: Tool Usage Tracker
# ─────────────────────────────────────────────

class ToolUsageTracker:
    """Track tool usage for analysis."""

    def __init__(self):
        self.usage_count: Dict[str, int] = {t.name: 0 for t in tools}
        self.tool_sequences: List[str] = []

    def record(self, tool_names: List[str]):
        for name in tool_names:
            if name in self.usage_count:
                self.usage_count[name] += 1
            self.tool_sequences.extend(tool_names)

    def get_statistics(self) -> Dict:
        return {
            "total_tool_calls": sum(self.usage_count.values()),
            "tool_counts": self.usage_count,
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
        response = handle_complaint(complaint)
        print(f"\nFINAL RESPONSE:\n{response}\n")

    print("\n" + "="*60)
    print("=== Tool Usage Analysis ===")
    stats = tracker.get_statistics()
    print(f"Complaints handled : {len(complaints)}")
    print(f"Tool usage counts  : {stats['tool_counts']}")
    print(f"Most used tool     : {stats['most_used']}")
    print("="*60)
