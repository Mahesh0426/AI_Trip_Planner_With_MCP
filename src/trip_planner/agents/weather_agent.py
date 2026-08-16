import asyncio

from langchain_core.messages import AIMessage

from ..mcp_client import current_weather, forecast
from ..state import TravelState


# Weather Agent - 
# It will get the weather information using custom MCP tools
# custom_weather_mcp_server.py

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
