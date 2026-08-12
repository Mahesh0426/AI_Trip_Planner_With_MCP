import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

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

import asyncio

async def main():

    tools = await client.get_tools()

    print("\nAvailable Tools:\n")

    for tool in tools:
        print(tool.name)

if __name__ == "__main__":
    asyncio.run(main())