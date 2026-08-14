import os
import sys
import asyncio
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
# MultiServerMCPClient is a LangChain adapter that knows how to communicate with MCP servers.

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Resolve virtualenv Python path dynamically (bin/python on Mac/Linux, Scripts/python.exe on Windows)
venv_python = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "aviationstack-mcp",
        ".venv",
        "Scripts" if os.name == "nt" else "bin",
        "python.exe" if os.name == "nt" else "python"
    )
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

# creating two variables for tavily_search tool and aviation tools
search_tool = None 
aviation_tools={}    # store 3 tools : list_airpots, list_airlines, search_flights
weather_tools={}

# initialization guard - it ensure that the mcp server is initialized only once
async def initialize_mcp():
    
    global search_tool
    global aviation_tools
    
    if search_tool is not None and aviation_tools:
        return
    
# get all the available tools
    tools = await client.get_tools()

    print("\nAvailable MCP Tools:")
    for tool in tools:
        print(tool.name)
        
    # Look all the tools and find the one whose name is tavily_search.
    search_tool = None
    for tool in tools:
        if tool.name == "tavily_search":
            search_tool = tool
            break
        
    # Take every tool, except tavily_search, and put it into a dictionary where the tool name is the key."
    aviation_tools = {
        tool.name: tool
        for tool in tools
        if tool.name != "tavily_search"
    }

# =========================
# Tavily MCP function
#=========================
async def tavily_mcp_server(query:str):
    await initialize_mcp()
    result = await search_tool.ainvoke({
        "query":query
    })
    return result

# =========================
# Aviation MCP function
#=========================
async def aviation_mcp_calls(tool_name: str, tool_args: dict = None):
    
     await initialize_mcp()
     tool = aviation_tools.get(tool_name)

     if not tool:
        return f"{tool_name} tool not found"

     return await tool.ainvoke(tool_args or {})

async def get_airports():
    await initialize_mcp()
    
    tool = aviation_tools.get("list_airports")
    
    if not tool:
        return "list_airpots tool not found"
    
    result = await tool.ainvoke({})
    return result

async def get_airlines():
    await initialize_mcp()
    
    tool = aviation_tools.get("list_airlines")
    
    if not tool:
        return "list_airlines tool not found"
    
    result = await tool.ainvoke({})
    return result


# =========================
# Weather MCP function
#=========================
weather_tool = None
forecast_tool = None

async def initialize_weather_tools():

    global weather_tool, forecast_tool

    if weather_tool is not None:
        return

    tools = await client.get_tools()

    weather_tool = next(
        t for t in tools
        if t.name == "get_current_weather"
    )

    forecast_tool = next(
        t for t in tools
        if t.name == "get_forecast"
    )

async def weather_mcp_search(city: str):

    await initialize_weather_tools()

    return await weather_tool.ainvoke(
        {
            "city": city
        }
    )

async def forecast_mcp_search(city: str):

    await initialize_weather_tools()

    return await forecast_tool.ainvoke(
        {
            "city": city
        }
    )

# LLM  - weather agent
llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

# ###################################
# Destination Extractor - to get city name for weather to fetch
# ###################################
def extract_destination(query: str):

    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """

    response = llm.invoke(prompt)

    return response.content.strip()



# testing all the available TOOLS
async def print_all_tools():
    tools = await client.get_tools()
    print(f"\nFound {len(tools)} MCP Tools:\n")
    for tool in tools:
        print(f"- {tool.name}")
       
if __name__ == "__main__":
    asyncio.run(print_all_tools())
