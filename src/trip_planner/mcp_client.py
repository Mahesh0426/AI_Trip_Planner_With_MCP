import os
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient
# MultiServerMCPClient is a LangChain adapter that knows how to communicate with MCP servers.
from .config import AVIATION_STACK_API_KEY, OPENWEATHER_API_KEY, TAVILY_API_KEY


# Resolve virtualenv Python path dynamically (bin/python on Mac/Linux, Scripts/python.exe on Windows)
# __file__ is at src/trip_planner/mcp_client.py → 2 levels up = AI-Trip-Planner-MCP/ (project root)
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
venv_python = os.path.join(
    _PROJECT_ROOT,
    "aviationstack-mcp",
    ".venv",
    "Scripts" if os.name == "nt" else "bin",
    "python.exe" if os.name == "nt" else "python"
)

# Create the MCP client for Tavily , AviationStack and Weather
client = MultiServerMCPClient(
    {
        "tavily":{
            "transport": "streamable_http", #tells the MCP client how it should communicate with the MCP server.
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },
         "aviationstack": {
            "transport": "stdio",
            "command": venv_python,
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
            }
        },
         "weather": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                "-m",
                "custom_weather_mcp_server",
                "mcp",
                "run"
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        },
    }
)

# Cache tools so we don't load them repeatedly
_tools_cache = None

async def get_tools():
    global _tools_cache

    if _tools_cache is None:
        try:
            _tools_cache = await client.get_tools()

        except Exception as e:
            print("\n========== FULL ERROR ==========")
            print(type(e))
            print(repr(e))

            if hasattr(e, "exceptions"):
                print("\nSUB EXCEPTIONS:")
                for i, sub in enumerate(e.exceptions):
                    print(f"\n--- Exception {i+1} ---")
                    print(type(sub))
                    print(repr(sub))

            raise

    return _tools_cache


async def call_tool(tool_name: str, args: dict = None):
    tools = await get_tools()

    tool = next(
        (tool for tool in tools
         if tool.name == tool_name),
        None,
    )

    if tool is None:
        raise ValueError(f"Tool '{tool_name}' not found")

    return await tool.ainvoke(args or {})


# ------------------------
# Tavily MCP Tools
# ------------------------
async def tavily_search(query: str):
    return await call_tool("tavily_search", {"query": query})

# ------------------------
# Aviation MCP Tools
# ------------------------
async def list_airports(search: str = "", limit: int = 10):
    return await call_tool("list_airports", {"search": search, "limit": limit, "offset": 0})


async def list_airlines(search: str = "", limit: int = 10):
    return await call_tool("list_airlines", {"search": search, "limit": limit, "offset": 0})

# ------------------------
# Weather MCP Tools
# ------------------------
async def current_weather(city: str):
    return await call_tool("get_current_weather", {"city": city})

async def forecast(city: str):
    return await call_tool("get_forecast", {"city": city})







