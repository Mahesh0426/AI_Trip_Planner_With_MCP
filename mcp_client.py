from streamlit.proto.NewSession_pb2 import Initialize
import os
import asyncio
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
# MultiServerMCPClient is a LangChain adapter that knows how to communicate with MCP servers.

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")

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

# Create the MCP client for Tavily and AviationStack
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
        }
    }
)

# tool discovery  | testing mcp server
async def main():
 
    tools = await client.get_tools()
    
    print("\nAvailable MCP tools:\n")
    for tool in tools:
            print(tool.name)
           
    
    # find the tavily_search tool from list of tools and break 
    search_tool = None
    for tool in tools:
        if tool.name == "tavily_search":
            search_tool = tool
            break

    # tool excution (tavily search tool call)
    result = await search_tool.ainvoke({
        "query": "Best hotel in sydney ?"
    })
    print("\nResult:", result)

# if __name__ == "__main__":
#     asyncio.run(main())


# initialize tavily mcp server only once
search_tool = None
aviation_tools={}

# Initialize mcp for both tavily and aviationstack 
async def initialize_mcp():
    
    global search_tool
    global aviation_tools
    
    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("\nAvailable MCP Tools:")

    for tool in tools:
        print(tool.name)
        
    # find the tavily_search tool from list of tools and break 
    search_tool = None
    for tool in tools:
        if tool.name == "tavily_search":
            search_tool = tool
            break
        
    # Get all the other tools of aviationstack using dict comprehension
    aviation_tools = {
        tool.name: tool
        for tool in tools
        if tool.name != "tavily_search"
    }


# function tavily_mcp_server -> using only this function we can call tavily mcp server
async def tavily_mcp_server(query:str):
    await initialize_mcp()
    result = await search_tool.ainvoke({
        "query":query
    })
    return result

# function for aviation mcp server 
async def aviation_mcp_calls(tool_name: str, tool_args: dict = None):
    tools = await client.get_tools()
    
    tool = next(
        t for t in tools
        if t.name == tool_name
    )
    
    result = await tool.ainvoke(tool_args or {})
    
    return result


# function to get list of airports from mcp tools
async def get_airports():
    await initialize_mcp()
    
    tool = aviation_tools.get("list_airpots")
    
    if not tool:
        return "list_airpots tool not found"
    
    result = await tool.ainvoke({})
    return result

# function to get list of airlines from mcp tools
async def get_airlines():
    await initialize_mcp()
    
    tool = aviation_tools.get("list_airlines")
    
    if not tool:
        return "list_airlines tool not found"
    
    result = await tool.ainvoke({})
    return result