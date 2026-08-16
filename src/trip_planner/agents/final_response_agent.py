from langchain_core.messages import AIMessage

from ..state import TravelState

from .base import _llm_text

# Final Agent - 
# It will produce the final polished travel plan.
def final_response_agent(state: TravelState):

    print("\n========== FINAL AGENT INPUT ==========")
    print("Approved:", state.get("approved"))
    print("Feedback:", state.get("human_feedback"))
    print("=======================================\n")

    if state["approved"]:
        prompt = f"""
The human approved this draft itinerary.

Produce the final polished travel plan.

Draft itinerary:
{state['itinerary']}

Budget notes:
{state['budget_results']}
"""
    else:
        prompt = f"""
The human did not approve the draft.

Original user request:
{state['user_query']}

Draft itinerary:
{state['itinerary']}

Human feedback:
{state['human_feedback']}

Budget notes:
{state['budget_results']}
"""

    result = _llm_text("You produce final user-ready travel plans.", prompt)

    print("\n========== FINAL RESPONSE ==========")
    print(result)
    print("====================================\n")

    return {
        "final_response": result,
        "messages": [AIMessage(content=result)],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
