from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ..schemas import SupervisorDecision
from ..state import TravelState

from .base import structured_llm

SUPERVISOR_SYSTEM_PROMPT = "You route work to specialist agents."

AGENT_DESCRIPTIONS = """
Available agents:
- flight_agent: used when flights, airports, airlines, routes, or airfare guidance are needed
- hotel_agent: use when hotels, stays, neighborhoods, or accommodation are needed
- weather_agent: use when weather, climate, season, packing, or forecast is useful
- budget_agent: use when budget, affordability, cost, or price constraints are mentioned
- itinerary_agent: almost always needed to produce the travel plan
"""


# Supervisor Agent - 
# It will decide which specialist agents are needed for the user's request.
# for eg : if user says "I want to plan a trip to Bali for 7 days with budget of $1000" 
# and if user has mentioned the budget then it will call the budget agent.
def supervisor_agent(state: TravelState):
    query = state["user_query"]

    prompt = f"""
    You are the supervisor of a real-world multi-agent travel planning system.
    Decide which specialist agents are needed for this user request.

    {AGENT_DESCRIPTIONS}

    User request:
    {query}
    """

    print("\n========== SUPERVISOR PROMPT ==========")
    print(prompt)
    print("========================================\n")

    # Automatically validates the output against SupervisorDecision schema
    decision: SupervisorDecision = structured_llm.invoke(
        [
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    print("\n========== PARSED SUPERVISOR DECISION ==========")
    print(decision.model_dump_json(indent=2))
    print("==================================================\n")

    return {
        "selected_agents": decision.selected_agents,
        "trip_constraints": decision.trip_constraints.model_dump(),
        "supervisor_reasoning": decision.reasoning,
        "messages": [AIMessage(content="Supervisor created the agent plan.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
