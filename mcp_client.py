from streamlit.proto.NewSession_pb2 import Initialize
import os
import asyncio
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
# MultiServerMCPClient is a LangChain adapter that knows how to communicate with MCP servers.

load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Tavily MCP Server
#        │
#        │ "Here are my tools"
#        ▼
# MultiServerMCPClient
#        │
#        │ converts MCP → LangChain
#        ▼
# LangChain StructuredTool objects


# Create the MCP client for Tavily
client = MultiServerMCPClient(
    {
        "tavily":{
            "transport": "streamable_http", #tells the MCP client how it should communicate with the MCP server.
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        }
    }
)

# tool calling from langhchain to tavily using mcp_server
async def main():
    # getting all tools from tavily
    tools = await client.get_tools()
    
    # print("\nAvailable MCP tools:\n", tools)
        # for tool in tools:
        #     print(tool.name)
    #output - tavily_search, tavily_extract, tavily_crawl, tavily_map,tavily_research
    
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


if __name__ == "__main__":
    asyncio.run(main())


# initialize tavily mcp server only once
search_tool = None

# initialize_mcp function is used to initialize the tavily mcp server only once 
# and get the tavily_search tool from the list of tools.
async def initialize_mcp():
    global search_tool
    if search_tool is not None:
        return

    tools = await client.get_tools()
    print("\nAvailable MCP Tools:")

    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )


#  function tavily_mcp_server -> using only this function we can call tavily mcp server
async def tavily_mcp_server(query:str):
    await initialize_mcp()
    result = await search_tool.ainvoke({
        "query":query
    })
    return result
    