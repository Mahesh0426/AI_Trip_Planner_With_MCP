import asyncio

from ..mcp_client import tavily_search
from ..state import TravelState

# Hotel Agent - 
# It will call the Tavily MCP tool to get hotel info.
def hotel_agent(state: TravelState):
    query = f"Best hotels and areas to stay for: {state['user_query']}"

    print("\n========== HOTEL AGENT INPUT ==========")
    print(query)
    print("=======================================\n")

    result = asyncio.run(tavily_search(query))

    print("\n========== HOTEL SEARCH RESULT ==========")
    print(result)
    print("=========================================\n")

    return {
        "hotel_results": str(result),
    }
