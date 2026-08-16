from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from ..state import TravelState

# Human Approval Agent - 
# It will pause the graph and ask the user for approval.
# Human approval is needed because we want the user to review the draft itinerary 
# and provide feedback before generating the final response.
def human_approval_agent(state: TravelState):
    feedback = interrupt(
        {
            "question": "Do you approve this itinerary?",
            "draft_itinerary": state.get("itinerary", ""),
            "approval_request": state.get("approval_request", ""),
            "expected_response": {
                "approved": True,
                "feedback": "Optional feedback for revision",
            },
        }
    )

    approved = feedback["approved"]
    human_feedback = feedback["feedback"]

    return {
        "approved": approved,
        "human_feedback": human_feedback,
        "messages": [AIMessage(content="Human approval step completed.")],
    }
