# ✈️ AI Trip Planner with MCP & LangGraph

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-v1.3+-green.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-v1.2+-orange.svg)](https://www.langchain.com/langgraph)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Supported-purple.svg)](https://modelcontextprotocol.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)

An autonomous, **multi-agent AI travel planning system** built with **LangGraph**, **Model Context Protocol (MCP)**, **Groq (LLaMA 3.3 70B)**, and **PostgreSQL** state persistence.

The system orchestrates a team of dedicated AI agents — supervised, coordinated, and approved by specialized control agents — to discover flights, search hotels, retrieve live weather forecasts, estimate budgets, and synthesize personalized, day-by-day travel itineraries.

---

## 🌟 Key Features

### 🤖 Multi-Agent Orchestration

Managed by a **LangGraph State Graph**, the system routes tasks intelligently across a full agent pipeline:

| Agent | Role | Tool / Backend |
| :--- | :--- | :--- |
| 🧠 **Supervisor Agent** | Analyzes the user query and dynamically selects which specialized agents are needed for the trip | Groq LLaMA 3.3 70B |
| 🛫 **Flight Agent** | Discovers airport codes, airline carriers, and flight route details | AviationStack MCP (`stdio`) |
| 🏨 **Hotel Agent** | Performs real-time web search for optimal accommodation options | Tavily MCP (`streamable_http`) |
| ☀️ **Weather Agent** | Retrieves live temperature, wind speed, and multi-period forecasts | Custom FastMCP (OpenWeatherMap) |
| 💰 **Budget Agent** | Estimates per-person and total trip costs, and generates a detailed expense breakdown | Groq LLaMA 3.3 70B |
| 📝 **Itinerary Agent** | Consolidates all agent outputs into a comprehensive, day-by-day travel plan | Groq LLaMA 3.3 70B |
| 👤 **Human Approval Agent** | Pauses execution and presents the draft itinerary to the user for review and approval | LangGraph `interrupt()` |
| 🎯 **Final Response Agent** | Polishes, formats, and delivers the final itinerary — incorporating user feedback if revisions were requested | Groq LLaMA 3.3 70B |

### ⚙️ Additional Capabilities

- **Dynamic Agent Selection**: The Supervisor Agent intelligently selects only the relevant agents required per query (e.g., a local trip may skip the flight agent).
- **Human-in-the-Loop Approval**: The workflow pauses after draft itinerary generation and resumes based on user approval or feedback, using LangGraph's `interrupt()` + `Command(resume=...)` pattern.
- **Model Context Protocol (MCP) Integration**:
  - **Tavily MCP**: Remote HTTP MCP (`streamable_http`) for real-time hotel & web search.
  - **AviationStack MCP**: Local subprocess (`stdio`) for real-time flight, airport, and airline details.
  - **Custom Weather MCP**: FastMCP Python server (`stdio`) backed by OpenWeatherMap API.
- **Stateful Session Checkpointing**: Built-in session persistence using `psycopg` and `langgraph-checkpoint-postgres` with a local Docker PostgreSQL container.
- **Dynamic Graph Visualization**: Generates a Mermaid workflow diagram (`graph1.png`) on startup.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Start([User Travel Query]) --> Supervisor[🧠 Supervisor Agent<br/><i>Selects required agents</i>]

    Supervisor -->|dynamic routing| FlightAgent[🛫 Flight Agent<br/><i>AviationStack MCP</i>]
    Supervisor -->|dynamic routing| HotelAgent[🏨 Hotel Agent<br/><i>Tavily MCP</i>]
    Supervisor -->|dynamic routing| WeatherAgent[☀️ Weather Agent<br/><i>Custom OpenWeather MCP</i>]
    Supervisor -->|dynamic routing| BudgetAgent[💰 Budget Agent<br/><i>LLaMA 3.3 70B</i>]

    FlightAgent --> ItineraryAgent[📝 Itinerary Agent<br/><i>LLaMA 3.3 70B</i>]
    HotelAgent --> ItineraryAgent
    WeatherAgent --> ItineraryAgent
    BudgetAgent --> ItineraryAgent

    ItineraryAgent --> HumanApproval[👤 Human Approval Agent<br/><i>interrupt — Awaits user review</i>]
    HumanApproval -->|approved| FinalAgent[🎯 Final Response Agent<br/><i>LLM Formatting</i>]
    HumanApproval -->|revision requested| FinalAgent
    FinalAgent --> End([✅ Final Detailed Itinerary])

    subgraph State Persistence
        Postgres[(PostgreSQL Checkpointer)] <--> Supervisor
        Postgres <--> FlightAgent
        Postgres <--> HotelAgent
        Postgres <--> WeatherAgent
        Postgres <--> BudgetAgent
        Postgres <--> ItineraryAgent
    end
```

---

## 🔌 MCP Tools Breakdown

| Server                 | Transport         | Tool Name             | Description                                                    |
| :--------------------- | :---------------- | :-------------------- | :------------------------------------------------------------- |
| **Tavily MCP**         | `streamable_http` | `tavily_search`       | Real-time web search for hotel listings and local attractions. |
| **AviationStack MCP**  | `stdio`           | `list_airports`       | Resolves departure/arrival airport codes and details.          |
| **AviationStack MCP**  | `stdio`           | `list_airlines`       | Queries active airline carriers for flight route planning.     |
| **Custom Weather MCP** | `stdio`           | `get_current_weather` | Retrieves live temperature, wind speed, and weather condition. |
| **Custom Weather MCP** | `stdio`           | `get_forecast`        | Fetches 5-period weather forecast data for destination city.   |

---

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.10+**
- **Docker Desktop** & **Docker Compose**
- **UV** (Python package manager)
- API Keys for external services:
  - **Groq API Key**: [console.groq.com](https://console.groq.com)
  - **Tavily API Key**: [tavily.com](https://www.tavily.com/)
  - **AviationStack API Key**: [aviationstack.com](https://aviationstack.com/)
  - **OpenWeatherMap API Key**: [openweathermap.org](https://openweathermap.org/)

---

## 🚀 Quickstart Guide

### 1. Clone the Repository

```bash
git clone https://github.com/Mahesh0426/AI_Trip_Planner_With_MCP.git
cd AI_Trip_Planner_With_MCP
```

> **Note**: Also clone the `aviationstack-mcp` subpackage inside the project root for the AviationStack MCP server:
>
> ```bash
> git clone https://github.com/Pradumnasaraf/aviationstack-mcp.git
> cd aviationstack-mcp
> ```

### 2. Install UV and Sync Dependencies

Check if UV is already installed:

```bash
uv --version
```

Install UV if needed:

```bash
pip install uv
```

Sync project dependencies with UV:

```bash
uv sync
```

### 3. Set Up Virtual Environment (Alternative to UV)

```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows (Command Prompt)
# venv\Scripts\activate
```

Install dependencies via pip:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp example.env .env
```

Fill in your API keys and database configuration in `.env`:

```env
# LLM
GROQ_API_KEY=your_groq_api_key

# MCP API Keys
TAVILY_API_KEY=your_tavily_api_key
AVIATION_STACK_API_KEY=your_aviationstack_api_key
OPENWEATHER_API_KEY=your_openweather_api_key

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=trip_planner
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/trip_planner
```

---

## 🐳 Running the Database with Docker

Start PostgreSQL in detached mode:

```bash
docker compose up -d
```

Verify the container is running:

```bash
docker compose ps
```

Stop the container when finished:

```bash
docker compose down
```

---

## 🏃 Running the Application

Ensure the Docker PostgreSQL container is active, then run:

```bash
python main.py
```

### Workflow Execution Flow

1. **Enter your travel query** when prompted:
   > _"Plan a 5-day trip to Tokyo from Sydney next month with a budget of $3000."_

2. **Supervisor Agent** analyzes the query and selects the relevant agents.

3. **Selected Agents run in sequence**:
   - 🛫 Queries airport & airline data via **AviationStack MCP**
   - 🏨 Fetches hotel recommendations via **Tavily MCP**
   - ☀️ Retrieves live weather & forecast via **Custom Weather MCP**
   - 💰 Estimates trip budget and cost breakdown

4. **Itinerary Agent** synthesizes all results into a draft travel plan.

5. **Human Approval Agent** pauses and presents the draft for your review:
   - If **approved** → final itinerary is generated and displayed.
   - If **rejected** → provide feedback and the final agent incorporates your revisions.

6. The **workflow graph** is saved as `graph1.png` on startup.

---

## 🧪 Testing Individual MCP Servers

Test individual MCP servers using the included test scripts:

- **Test Weather MCP Server**:

  ```bash
  python test_mcp/testing_weather_mcp.py
  ```

- **Test AviationStack MCP Server**:

  ```bash
  python test_mcp/testing_aviationstack_mcp_server.py
  ```

---

## 📂 Project Structure

```
├── main.py                                     # Application entrypoint — runs the LangGraph pipeline
├── custom_weather_mcp_server.py                # FastMCP server integrating OpenWeatherMap API
├── pyproject.toml                              # Project metadata and dependencies (UV)
├── requirements.txt                            # Python dependencies (pip fallback)
├── example.env                                 # Template environment variable configuration
├── graph1.png                                  # Generated LangGraph visual workflow diagram
├── infra/                                      # Infrastructure configs (Docker, DB)
├── test_mcp/                                   # MCP server test scripts
│   ├── testing_weather_mcp.py
│   └── testing_aviationstack_mcp_server.py
├── tests/                                      # Unit and integration tests
├── aviationstack-mcp/                          # AviationStack MCP server subpackage
└── src/
    └── trip_planner/
        ├── __init__.py
        ├── graph.py                            # LangGraph state graph definition & compilation
        ├── state.py                            # TravelState TypedDict schema
        ├── schemas.py                          # Pydantic models and structured output schemas
        ├── config.py                           # Environment variable loading
        ├── mcp_client.py                       # MultiServerMCPClient manager (Tavily, AviationStack, Weather)
        ├── guardrails/                         # Input validation and guardrails
        └── agents/
            ├── __init__.py
            ├── base.py                         # Shared agent utilities and base class
            ├── supervisor_agent.py             # 🧠 Analyzes query & selects required agents
            ├── flight_agent.py                 # 🛫 Queries flights via AviationStack MCP
            ├── hotel_agent.py                  # 🏨 Searches hotels via Tavily MCP
            ├── weather_agent.py                # ☀️ Fetches weather via Custom MCP
            ├── budget_agent.py                 # 💰 Estimates trip costs & budget breakdown
            ├── itinerary_agent.py              # 📝 Synthesizes all results into a travel plan
            ├── human_approval_agent.py         # 👤 Pauses graph for user review & approval
            └── final_response_agent.py         # 🎯 Formats and delivers the final itinerary
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Database Connection Refused** | Ensure Docker Desktop is running and execute `docker compose up -d`. Verify `POSTGRES_PORT` in `.env` matches `docker-compose.yml` (default `5433`). |
| **MCP Server Launch Failure** | Check that the virtual environment Python path in `mcp_client.py` is correct and the venv is activated. |
| **Missing API Keys** | Verify `.env` exists in the root directory with valid keys for Groq, Tavily, AviationStack, and OpenWeatherMap. |
| **Graph Not Resuming After Approval** | Ensure `thread_id` in `config` matches the original run so LangGraph can restore checkpointed state from PostgreSQL. |
| **UV Sync Fails** | Ensure `uv` is installed (`pip install uv`) and `pyproject.toml` is present in the project root. |

---

## 📄 License

This project is open-source. See repository details for license information.
