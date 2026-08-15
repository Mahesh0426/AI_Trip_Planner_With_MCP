import warnings
warnings.filterwarnings("ignore")

import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(override=True)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in environment variables. Please check your .env file.")

# Create the MCP client for Tavily
client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        }
    }
)

async def main():
    print("Loading Tavily MCP tools...")
    tools = await client.get_tools()
    print("Tools loaded successfully!\n")

    print("Available Tools:")
    for tool in tools:
        print(f"- {tool.name}")

    # Find the tavily_search tool
    # tavily_tool = next(
    #     (tool for tool in tools
    #      if tool.name == "tavily_search"),
    #     None
    # )
    tavily_tool = None
    for tool in tools:
        if tool.name == "tavily_search":
            tavily_tool = tool
            break

    if not tavily_tool:
        print("\nError: 'tavily_search' tool not found among available tools.")
        return

    # Call the MCP tool
    test_query = "Top tourist attractions in Sydney"
    print(f"\nExecuting search query: '{test_query}'...\n")

    result = await tavily_tool.ainvoke({"query": test_query})
    print("Search Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
