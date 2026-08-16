from langchain_core.messages import HumanMessage
from langgraph.types import Command

from trip_planner.graph import build_graph

# run the graph
if __name__ == "__main__":
    app = build_graph()  # Build and compile the graph

    config = {
        "configurable": {
            "thread_id": "mahesh-4"  # Required for resuming state
        }
    }

    # every run fresh start
    # import uuid
    # config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    user_input = input("Enter travel request: ").strip()

    # Basic validation — reject shell commands or empty inputs
    SHELL_KEYWORDS = ("source ", "export ", "cd ", "ls ", "echo ", "cat ", "python", "./", "activate")
    if not user_input or len(user_input) < 10 or any(user_input.startswith(kw) for kw in SHELL_KEYWORDS):
        print("\n❌ Invalid travel request. Please describe your trip (e.g. 'Plan a 5-day trip to Tokyo').")
        exit(1)

    print("\n⏳ Running agents... please wait...\n")

    # ── PHASE 1: First invoke ──────────────────────────────────────────────────
    # The graph will run all agents and then PAUSE at human_approval_agent's
    # interrupt() call. State is saved to Postgres automatically.
    result = app.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0,
        },
        config=config,
    )

    # Check if the graph paused at an interrupt (human approval needed)
    # When interrupted, LangGraph adds an "__interrupt__" key to the result
    if "__interrupt__" in result:
        interrupt_payload = result["__interrupt__"][0].value

        # Show the draft itinerary to the user
        print("\n" + "=" * 60)
        print("📋  DRAFT ITINERARY — PLEASE REVIEW")
        print("=" * 60)
        print(interrupt_payload.get("draft_itinerary", ""))
        print("=" * 60 + "\n")

        # ── PHASE 2: Ask for approval ──────────────────────────────────────────
        approval = input("Do you approve this itinerary? (yes/no): ").strip().lower()
        approved = approval in ("yes", "y")

        feedback = ""
        if not approved:
            feedback = input(
                "Please provide your feedback for revision: "
            ).strip()

        print("\n⏳ Generating final response...\n")

        # Resume the graph by sending the human's decision back via Command
        final_result = app.invoke(
            Command(
                resume={
                    "approved": approved,
                    "feedback": feedback,
                }
            ),
            config=config,
        )

        print("\n" + "=" * 60)
        print("✅  FINAL RESPONSE")
        print("=" * 60)
        for msg in final_result["messages"]:
            print(msg.content)

    else:
        # Graph completed without interruption (shouldn't happen normally)
        print("\nFINAL RESPONSE:\n")
        for msg in result["messages"]:
            print(msg.content)
