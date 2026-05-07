# Lab Summary — NormalObjects Creative Complaint Handler (LangChain)

The LangChain agent used its tools in a genuinely exploratory way: for a complaint about
demogorgon behaviour it might call `consult_demogorgon` first, then pivot to
`gather_party_wisdom` and finish with `cast_interdimensional_spell`, while for a portal
question it started with `check_hawkins_records` before consulting the party — the order
emerged from the LLM's own reasoning rather than from any fixed rule. This freeform
chaining is the key difference from a structured LangGraph workflow, where every edge
between nodes is declared in advance and the execution path is deterministic and auditable.
The LangChain approach is well-suited to open-ended, creative tasks where you want the
agent to decide on-the-fly which tools are relevant; LangGraph is the better choice when
you need guaranteed execution order, strict error recovery, human-in-the-loop steps, or
compliance-level traceability — scenarios where "the agent just decided to skip a step"
would be unacceptable.
