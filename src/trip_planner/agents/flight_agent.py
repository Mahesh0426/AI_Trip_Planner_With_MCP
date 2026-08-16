import asyncio

from langchain_core.messages import AIMessage

from ..mcp_client import list_airlines, list_airports
from ..state import TravelState

from .base import _llm_text

# Flight Agent - 
# It will call the AviationStack MCP local tool to get flight information.
# aviationstack-mcp - https://github.com/AviationStack/ AviationStack MCP

def flight_agent(state: TravelState):
    query = state["user_query"]
    constraints = state["trip_constraints"]
    destination = constraints["destination"]

    print("\n========== FLIGHT AGENT INPUT ==========")
    print("Query:", query)
    print("Constraints:", constraints)
    print("========================================\n")

    airports = asyncio.run(list_airports(destination, limit=10))
    airlines = asyncio.run(list_airlines("", limit=10))

    print("\n========== AIRPORT MCP DATA ==========")
    print(airports)
    print("======================================\n")

    print("\n========== AIRLINE MCP DATA ==========")
    print(airlines)
    print("======================================\n")

    prompt = f"""
Create flight guidance for this trip.

User request:
{query}

Trip constraints:
{constraints}

Airport MCP data:
{str(airports)[:3000]}

Airline MCP data:
{str(airlines)[:3000]}

Include likely departure/arrival airports, relevant airlines,
estimated duration, fare range, peak season warning,
and booking advice.
"""

    result = _llm_text("You are a flight planning specialist.", prompt)

    print("\n========== FLIGHT AGENT OUTPUT ==========")
    print(result)
    print("=========================================\n")

    return {
        "flight_results": result,
        "messages": [AIMessage(content="Flight agent completed.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
