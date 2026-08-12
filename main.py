import os
from typing import TypedDict, Annotated
import operator
import asyncio

import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq
# from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from dotenv import load_dotenv
from mcp_client import tavily_mcp_server

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/trip_planner")

# Note: Make sure your Docker container is running (`docker compose up -d`) before connecting.
# Example PostgresSaver connection setup:
# with psycopg.connect(DB_URI, autocommit=True) as conn:
#     checkpointer = PostgresSaver(conn)
#     checkpointer.setup()  # Call setup() on first run to initialize checkpoint tables

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

#TravelState is the shared storage that every node in your LangGraph can read from and write to
class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]  # List of messages; operator.add combines new messages with existing messages.
    user_query: str 
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
    
    
# Flight Agent
def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data = search_flights(query)
    
    #update TravelState with below details
    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content=f"Flight results fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
    
    # Hotel Agent
def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    # hotel_results = tavily_search(query)
    
    # using from mcp
    hotel_results = asyncio.run(tavily_mcp_server(query))

    #update TravelState with below details
    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(content="Hotel information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
    
# Itinerary Agent
def itinerary_agent(state: TravelState):

    # dynamic prompt to send to the llm
    prompt = f"""
    Create a travel itinerary.
    User Query:
    {state['user_query']}

    Flight Results:
    {state['flight_results']}

    Hotel Results:
    {state['hotel_results']}
    """

    # call the llm
    response = llm.invoke([
        SystemMessage(
            content="You are an expert travel planner"
        ),
        HumanMessage(content=prompt)
    ])

# update TravelState with below details
    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# Final Response Agent
def final_agent(state: TravelState):

    # dynamic final prompt to send to the llm
    final_prompt = f"""
    Generate final travel response and aslo add relatable emoji.

    Flights:
    {state['flight_results']}

    Hotels:
    {state['hotel_results']}

    Itinerary:
    {state['itinerary']}
    """

#llm call
    response = llm.invoke([
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# Build the graph
g = StateGraph(TravelState)

# add nodes
g.add_node("flight_agent", flight_agent)
g.add_node("hotel_agent", hotel_agent)
g.add_node("itinerary_agent", itinerary_agent)
g.add_node("final_agent", final_agent)

# add edges
g.add_edge(START , "flight_agent")
g.add_edge("flight_agent", "hotel_agent")
g.add_edge("hotel_agent", "itinerary_agent")
g.add_edge("itinerary_agent", "final_agent")
g.add_edge("final_agent", END)


# Persistent connection so both CLI and Streamlit can share the compiled app
_conn = psycopg.connect(DATABASE_URL, autocommit=True)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

# compile the graph
app = g.compile(checkpointer=checkpointer)

# save graph to file
save_path = "graph.png"
png_data = app.get_graph().draw_mermaid_png()
with open(save_path, "wb") as f:
    f.write(png_data)
print("Graph saved successfully!")


# run the graph
if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "mahesh-2"  # Required for resuming state
        }
    }

    #every run fresh start
    # import uuid
    # config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    user_input = input("Enter travel requests:")
    
    # Invoke the multi-agent graph with initial state and session config for Postgres checkpoint persistence
    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("\nFINAL RESPONSE:\n")

    for msg in result["messages"]:
        print(msg.content)




# query ="Create a five-day plan for Melbourne. I'm visiting Melbourne from Sydney."
# result = g.invoke({
#     'user_query': query,
#     "flight_results" :"",
#     "hotel_results":"",
#     'itinerary':"",
#     'messages':[],
#     'llm_calls':0
# })

# print("\nQUERY:",query)
# print("Final response:",result["messages"][-1].content)
# print("Total LLM calls:", result["llm_calls"])


