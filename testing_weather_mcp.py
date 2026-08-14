import warnings
warnings.filterwarnings("ignore")
import os
from dotenv import load_dotenv
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(override=True)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

import sys 
# sys is a built-in Python module that gives you information and control over the Python runtime.

venv_python = sys.executable

client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "stdio",
            "command": venv_python,
            "args": [
                "-m",
                "custom_weather_mcp_server",
                "mcp",
                "run"
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        }
    }
)

async def main():

    print("Loading Weather MCP tools...\n")
    tools = await client.get_tools()
    print("Tools loaded successfully!")

    print("\nAvailable Tools:")
    for tool in tools:
        print(f"- {tool.name}")
        
    # Find the weather tool
    weather_tool = next(
        tool for tool in tools
        if tool.name == "get_current_weather"
    )
    # Call the MCP tool
    result = await weather_tool.ainvoke(
        {"city": "Sydney"}
    )
    print("\nSydney Weather:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

