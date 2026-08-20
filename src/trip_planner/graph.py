import psycopg
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph

from .agents import (
    budget_agent,
    final_response_agent,
    flight_agent,
    hotel_agent,
    human_approval_agent,
    itinerary_agent,
    supervisor_agent,
    weather_agent,
)
from .config import DATABASE_URL
from .state import TravelState

#define the order
AGENT_ORDER = [
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
]

ROUTE_MAP = {
    "flight_agent": "flight_agent",
    "hotel_agent": "hotel_agent",
    "weather_agent": "weather_agent",
    "budget_agent": "budget_agent",
    "itinerary_agent": "itinerary_agent",
}

# selecting agents according to the user input
def _selected_agents(state: TravelState) -> list[str]:
    selected = state.get("selected_agents")
    return [agent for agent in AGENT_ORDER if agent in selected]  

# selecting first agent from the AGENT_ORDER
# if no agent is selected, it will route to the itinerary agent
def route_from_supervisor(state: TravelState) -> str:
    selected = _selected_agents(state)
    return selected[0] if selected else "itinerary_agent"

# routing to the next agent in the AGENT_ORDER
def route_after_agent(current_agent: str):
    def route(state: TravelState) -> str:
        selected = _selected_agents(state)
        current_index = AGENT_ORDER.index(current_agent)

        for next_agent in AGENT_ORDER[current_index + 1:]:
            if next_agent in selected:
                return next_agent

        return "itinerary_agent"
    return route

# build the graph for travel planning agents
def build_graph():
    graph = StateGraph(TravelState)

    graph.add_node("supervisor", supervisor_agent)
    graph.add_node("flight_agent", flight_agent)
    graph.add_node("hotel_agent", hotel_agent)
    graph.add_node("weather_agent", weather_agent)
    graph.add_node("budget_agent", budget_agent)
    graph.add_node("itinerary_agent", itinerary_agent)
    graph.add_node("human_approval", human_approval_agent)
    graph.add_node("final_response", final_response_agent)
    
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route_from_supervisor, ROUTE_MAP)
    graph.add_conditional_edges("flight_agent", route_after_agent("flight_agent"), ROUTE_MAP)
    graph.add_conditional_edges("hotel_agent", route_after_agent("hotel_agent"), ROUTE_MAP)
    graph.add_conditional_edges("weather_agent", route_after_agent("weather_agent"), ROUTE_MAP)
    graph.add_conditional_edges("budget_agent", route_after_agent("budget_agent"), ROUTE_MAP)
    graph.add_edge("itinerary_agent", "human_approval")
    graph.add_edge("human_approval", "final_response")
    graph.add_edge("final_response", END)
    
    # Persistent connection so both CLI and Streamlit can share the compiled app
    if DATABASE_URL:
        conn = psycopg.connect(DATABASE_URL)
        checkpointer = PostgresSaver(conn)
        checkpointer.setup()
        
        # Compile the graph
        app = graph.compile(checkpointer=checkpointer)
    
    # Save graph diagram to PNG file
    try:
        save_path = "graph1.png"
        png_data = app.get_graph().draw_mermaid_png()
        with open(save_path, "wb") as f:
            f.write(png_data)
        print("Graph saved successfully!")
    except Exception as e:
        print(f"Could not save graph image: {e}")
    return app

