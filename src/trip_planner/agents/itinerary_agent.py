from langchain_core.messages import AIMessage

from ..state import TravelState

from .base import _llm_text

# Itinerary Agent - 
# It will create a draft itinerary based on the user's request and constraints.
def itinerary_agent(state: TravelState):

    print("\n========== ITINERARY AGENT INPUT ==========")
    print("Trip Constraints:")
    print(state.get("trip_constraints"))
    print("\nFlight Results:")
    print(state.get("flight_results"))
    print("\nHotel Results:")
    print(state.get("hotel_results"))
    print("\nWeather Results:")
    print(state.get("weather_results"))
    print("\nBudget Results:")
    print(state.get("budget_results"))
    print("===========================================\n")

    prompt = f"""
Create a clear draft travel itinerary.

User request:
{state['user_query']}

Trip constraints:
{state.get('trip_constraints', {})}

Flight results:
{state.get('flight_results', '')}

Hotel results:
{state.get('hotel_results', '')}

Weather results:
{state.get('weather_results', '')}

Budget results:
{state.get('budget_results', '')}

Make the output structured, practical, and ready for human review.
"""

    result = _llm_text("You are an expert itinerary planner.", prompt)

    print("\n========== ITINERARY OUTPUT ==========")
    print(result)
    print("======================================\n")

    approval_request = f"""
Please review this draft travel plan.

{result}

Reply with approval or feedback.
"""

    return {
        "itinerary": result,
        "approval_request": approval_request,
        "messages": [AIMessage(content="Draft itinerary created for human review.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
