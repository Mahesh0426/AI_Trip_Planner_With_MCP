import asyncio
import json
from typing import Any

from langchain_core.messages import ( AnyMessage,HumanMessage,AIMessage,SystemMessage)
from langgraph.types import interrupt

from config import get_llm
from mcp_client import (current_weather, forecast,list_airlines,list_airports,tavily_search)
from state import TravelState
from schemas import SupervisorDecision

llm = get_llm()



# helper function to call llm
def _llm_text(system:str,prompt:str)-> str:
    response = llm.invoke(
        [
            SystemMessage(content=system),
            HumanMessage(content=prompt)
        ]
    )
    return response.content

# function to convert response from llm to py dict
def _json_from_llm(text:str) -> dict:
    print("\n========== RAW LLM RESPONSE ==========")
    print(text)
    print("======================================\n")

    # search the first '{' and last '}' and extract the json
    start = text.index("{")
    end = text.rindex("}") + 1
    json_text = text[start:end]

    print("\n========== EXTRACTED JSON ==========")
    print(json_text)
    print("====================================\n")

    # return Load from a string to py dict
    return json.loads(json_text)
   
# structured llm with supervisor decision schema 
structured_llm = llm.with_structured_output(SupervisorDecision)

SUPERVISOR_SYSTEM_PROMPT = "You route work to specialist agents."

AGENT_DESCRIPTIONS = """
Available agents:
- flight_agent: used when flights, airports, airlines, routes, or airfare guidance are needed
- hotel_agent: use when hotels, stays, neighborhoods, or accommodation are needed
- weather_agent: use when weather, climate, season, packing, or forecast is useful
- budget_agent: use when budget, affordability, cost, or price constraints are mentioned
- itinerary_agent: almost always needed to produce the travel plan
""" 

# supervisor agent
def supervisor_agent(state: TravelState):
    query = state["user_query"]

    prompt = f"""
    You are the supervisor of a real-world multi-agent travel planning system.
    Decide which specialist agents are needed for this user request.

    {AGENT_DESCRIPTIONS}

    User request:
    {query}
    """

    print("\n========== SUPERVISOR PROMPT ==========")
    print(prompt)
    print("========================================\n")

    # this will automatically validate the output against SupervisorDecision schema
    decision: SupervisorDecision = structured_llm.invoke(
        [
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    print("\n========== PARSED SUPERVISOR DECISION ==========")
    print(decision.model_dump_json(indent=2))
    print("==================================================\n")

    return {
        "selected_agents": decision.selected_agents,
        "trip_constraints": decision.trip_constraints.model_dump(),
        "supervisor_reasoning": decision.reasoning,
        "messages": [AIMessage(content="Supervisor created the agent plan.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }

# flight agents 
def flight_agent(state:TravelState):
        query = state['user_query']
        constraints = state['trip_constraints']
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
       
        result = _llm_text(
        "You are a flight planning specialist.",
        prompt,
    )
        print("\n========== FLIGHT AGENT OUTPUT ==========")
        print(result)
        print("=========================================\n")
        
        return {
        "flight_results": result,
        "messages": [AIMessage(content="Flight agent completed.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }

# hotel agent
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
   
   
#  weather agent  
def weather_agent(state: TravelState):
    constraints = state["trip_constraints"]
    city = constraints["destination"]

    print("\n========== WEATHER AGENT INPUT ==========")
    print("City:", city)
    print("=========================================\n")

    weather_data = asyncio.run(current_weather(city))
    forecast_data = asyncio.run(forecast(city))

    print("\n========== CURRENT WEATHER ==========")
    print(weather_data)
    print("=====================================\n")

    print("\n========== WEATHER FORECAST ==========")
    print(forecast_data)
    print("======================================\n")

    result = f"""
Current weather:
{weather_data}

Forecast:
{forecast_data}
"""

    print("\n========== WEATHER AGENT OUTPUT ==========")
    print(result)
    print("==========================================\n")

    return {
        "weather_results": result,
        "messages": [AIMessage(content="Weather agent completed.")],
    }



        