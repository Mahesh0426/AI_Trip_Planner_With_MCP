"""Final Response Agent
Produces the final polished travel plan shown to the user.

Output guardrail
----------------
After the LLM generates the response, validate_output() from
guardrails/output_guard.py runs four checks:
  1. Not empty
  2. Not a refusal ("I'm sorry, I can't…")
  3. Minimum length (100 chars)
  4. Contains at least one travel keyword

If the response fails any check, an OutputGuardrailError is caught here
and a safe fallback message is returned to the user instead of crashing.
"""

from langchain_core.messages import AIMessage

from ..guardrails import OutputGuardrailError, validate_output
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
{state.get('budget_results', 'N/A')}
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
{state.get('budget_results', 'N/A')}
"""

    raw_result = _llm_text("You produce final user-ready travel plans.", prompt)

    print("\n========== FINAL RESPONSE (RAW) ==========")
    print(raw_result)
    print("==========================================\n")

    # ── Output guardrail ──────────────────────────────────────────────────────
    # validate_output() is imported from guardrails/output_guard.py.
    # It checks: not empty, not a refusal, minimum length, travel content.
    # On failure we catch OutputGuardrailError and return a safe fallback
    # so the user always gets a meaningful message rather than an exception.
    try:
        result = validate_output(raw_result)
        print("✅ Output guardrail passed.")
    except OutputGuardrailError as exc:
        print(f"\n❌ OUTPUT GUARDRAIL REJECTED: {exc}\n")
        result = (
            "⚠️ We were unable to generate a valid travel plan at this time. "
            f"Reason: {exc}\n\n"
            "Please try again or rephrase your request."
        )

    print("\n========== FINAL RESPONSE (VALIDATED) ==========")
    print(result)
    print("=================================================\n")

    return {
        "final_response": result,
        "messages": [AIMessage(content=result)],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
