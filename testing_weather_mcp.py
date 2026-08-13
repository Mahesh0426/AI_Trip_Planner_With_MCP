import os
from dotenv import load_dotenv
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
#load_dotenv()
load_dotenv(override=True)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
venv_python = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "aviationstack-mcp",
        ".venv",
        "Scripts" if os.name == "nt" else "bin",
        "python.exe" if os.name == "nt" else "python"
    )
)

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

    print("Loading tools...")

    tools = await client.get_tools()

    print("Tools loaded!")

    for tool in tools:
        print(tool.name)

if __name__ == "__main__":
    asyncio.run(main())