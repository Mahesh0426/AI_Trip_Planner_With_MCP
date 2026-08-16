from langchain_core.messages import AIMessage

from ..state import TravelState

from .base import _llm_text

# This is a Budget Agent 
# It will analyze whether the trip plan is realistic for the user's budget.
def budget_agent(state: TravelState):

    print("\n========== BUDGET AGENT INPUT ==========")
    print("Trip Constraints:")
    print(state.get("trip_constraints"))
    print("\nFlight Results:")
    print(state.get("flight_results"))
    print("\nHotel Results:")
    print(state.get("hotel_results"))
    print("\nWeather Results:")
    print(state.get("weather_results"))
    print("=========================================\n")

    prompt = f"""
Analyze whether this trip plan is realistic for the user's budget.

User request:
{state['user_query']}

Constraints:
{state.get('trip_constraints', {})}

Flight results:
{state.get('flight_results', '')}

Hotel results:
{state.get('hotel_results', '')}

Weather results:
{state.get('weather_results', '')}

Return a concise budget assessment with:
1. estimated cost categories
2. risk areas
3. money-saving suggestions
4. whether the plan seems feasible
"""

    result = _llm_text("You are a practical travel budget analyst.", prompt)

    print("\n========== BUDGET AGENT OUTPUT ==========")
    print(result)
    print("=========================================\n")

    return {
        "budget_results": result,
        "messages": [AIMessage(content="Budget agent completed.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
