import os
import json
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import sys 
load_dotenv()

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

client = MultiServerMCPClient(
    {
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

async def main():
    print("Loading Aviation MCP tools...\n")
    tools = await client.get_tools()
    print("Tools loaded successfully!")

    print("\nAvailable Tools:\n")
    for tool in tools:
        print(f"- {tool.name}")

    # Find aviation flight tool
    tools_dict = {tool.name: tool for tool in tools}

    if "flights_with_airline" in tools_dict:
        print("\n--- Testing 'flights_with_airline' Tool ---")
        result = await tools_dict["flights_with_airline"].ainvoke(
            {"airline_name": "Singapore Airlines", "number_of_flights": 3}
        )
        print("Flight Search Result:")
        for item in result:
            if isinstance(item, dict) and "text" in item:
                try:
                    parsed = json.loads(item["text"])
                    print(json.dumps(parsed, indent=2))
                except Exception:
                    print(item["text"])
            else:
                print(item)

if __name__ == "__main__":
    asyncio.run(main())