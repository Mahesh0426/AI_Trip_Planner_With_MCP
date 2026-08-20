"""Supervisor Agent
Orchestrates the multi-agent travel planning pipeline.

How the guardrail connects
--------------------------
This node is the FIRST node in the LangGraph graph (START → supervisor).
Before doing any expensive agent routing, it calls validate_input() from
the guardrails package, which runs two layers of checks:

  Layer 1 (no LLM): length check + shell/code keyword detection
  Layer 2 (LLM):    travel-relevance check — rejects "write code", "order pizza", etc.

If validate_input() raises GuardrailError, the supervisor short-circuits:
it returns selected_agents=[] and an error message, so NO specialist agents
are ever called.

If the query passes, the supervisor uses structured_llm to decide which
specialist agents are needed and extracts trip constraints.

The guardrail logic lives in guardrails/input_guard.py so it can be
tested and reused independently of the supervisor.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Import GuardrailError and validate_input from the guardrails package
# (src/trip_planner/guardrails/input_guard.py)
from ..guardrails import GuardrailError, validate_input
from ..schemas import SupervisorDecision
from ..state import TravelState
from .base import structured_llm


# ──────────────────────────────────────────────────────────────────────────────
# Prompts
# ──────────────────────────────────────────────────────────────────────────────

SUPERVISOR_SYSTEM_PROMPT = "You route work to specialist agents."

AGENT_DESCRIPTIONS = """\
Available agents:
- flight_agent: used when flights, airports, airlines, routes, or airfare guidance are needed
- hotel_agent: use when hotels, stays, neighborhoods, or accommodation are needed
- weather_agent: use when weather, climate, season, packing, or forecast is useful
- budget_agent: use when budget, affordability, cost, or price constraints are mentioned
- itinerary_agent: almost always needed to produce the travel plan
"""

_ROUTING_PROMPT_TEMPLATE = """\
You are the supervisor of a real-world multi-agent travel planning system.
Decide which specialist agents are needed for this user request.

{agent_descriptions}

User request:
{query}
"""


# ──────────────────────────────────────────────────────────────────────────────
# Supervisor node
# ──────────────────────────────────────────────────────────────────────────────

def supervisor_agent(state: TravelState) -> dict:
    """
    LangGraph node: validates the query via guardrails, then routes to agents.

    Step 1 — Input guardrail (guardrails/input_guard.py):
        validate_input() runs two layers:
          - Heuristic: length / shell-keyword checks (fast, no LLM)
          - LLM check: is this actually a travel planning request?
        If it raises GuardrailError → return an error state immediately.

    Step 2 — Agent routing:
        structured_llm selects which specialist agents to call and extracts
        trip constraints (destination, budget, duration, etc.).

    Returns a partial TravelState update dict.
    """
    raw_query: str = state["user_query"]

    # ── Step 1: Input guardrail ───────────────────────────────────────────────
    # validate_input is imported from guardrails/input_guard.py.
    # GuardrailError is a subclass of ValueError — catch it specifically so we
    # can return a clean rejection instead of crashing the graph.
    try:
        clean_query = validate_input(raw_query, use_llm=True)
    except GuardrailError as exc:
        reason = str(exc)
        print(f"\n❌ INPUT GUARDRAIL REJECTED: {reason}\n")
        # Short-circuit: return empty agents list so the graph routes nowhere
        return {
            "selected_agents": [],
            "trip_constraints": {},
            "supervisor_reasoning": reason,
            "messages": [
                AIMessage(
                    content=f"❌ Your request was rejected by the input guardrail:\n{reason}"
                )
            ],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    # ── Step 2: Agent routing ─────────────────────────────────────────────────
    # Use structured output to enforce the SupervisorDecision schema so we
    # always get a validated list of agents + trip constraints.
    prompt = _ROUTING_PROMPT_TEMPLATE.format(
        agent_descriptions=AGENT_DESCRIPTIONS,
        query=clean_query,
    )

    print("\n========== SUPERVISOR ROUTING PROMPT ==========")
    print(prompt)
    print("===============================================\n")

    decision: SupervisorDecision = structured_llm.invoke(
        [
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    print("\n========== SUPERVISOR DECISION ==========")
    print(decision.model_dump_json(indent=2))
    print("=========================================\n")

    return {
        "selected_agents": decision.selected_agents,
        "trip_constraints": decision.trip_constraints.model_dump(),
        "supervisor_reasoning": decision.reasoning,
        "messages": [AIMessage(content="✅ Supervisor created the agent plan.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
