# ✈️ AI Trip Planner with MCP & LangGraph

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-v1.3+-green.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-v1.2+-orange.svg)](https://www.langchain.com/langgraph)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Supported-purple.svg)](https://modelcontextprotocol.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)

An autonomous, multi-agent AI travel planning system built with **LangGraph**, **Model Context Protocol (MCP)**, **Groq (LLaMA 3.3 70B)**, and **PostgreSQL** state persistence.

The system coordinates dedicated AI agents to discover flights, search hotels, retrieve live weather forecasts, and synthesize personalized, day-by-day travel itineraries.

---

## 🌟 Key Features

- **Multi-Agent Orchestration**: Managed by **LangGraph** State Graph, routing tasks sequentially across specialized agents:
  - 🛫 **Flight Agent**: Analyzes airport and airline data via AviationStack MCP.
  - 🏨 **Hotel Agent**: Performs real-time web search for optimal accommodations using Tavily MCP.
  - ☀️ **Weather Agent**: Queries live temperature and forecasts using a Custom FastMCP server.
  - 📝 **Itinerary Agent**: Consolidates all agent outputs into a comprehensive travel plan.
  - 🎯 **Final Agent**: Polishes and formats the final itinerary with travel tips and rich formatting.
- **Model Context Protocol (MCP) Integration**:
  - **Tavily MCP**: Remote HTTP MCP (`streamable_http`) for real-time hotel & web search.
  - **AviationStack MCP**: Local subprocess (`stdio`) for real-time flight, airport, and airline details.
  - **Custom Weather MCP**: FastMCP Python server (`stdio`) backed by OpenWeatherMap API.
- **Stateful Session Checkpointing**: Built-in session persistence using `psycopg` and `langgraph-checkpoint-postgres` with local Docker PostgreSQL container.
- **Dynamic Graph Visualization**: Generates a Mermaid workflow graph (`graph.png`) upon application startup.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Start([User Travel Query]) --> FlightAgent[Flight Agent<br/><i>AviationStack MCP</i>]
    FlightAgent --> HotelAgent[Hotel Agent<br/><i>Tavily MCP</i>]
    HotelAgent --> WeatherAgent[Weather Agent<br/><i>Custom OpenWeather MCP</i>]
    WeatherAgent --> ItineraryAgent[Itinerary Agent<br/><i>LLaMA 3.3 70B</i>]
    ItineraryAgent --> FinalAgent[Final Response Agent<br/><i>LLM Formatting</i>]
    FinalAgent --> End([Final Detailed Itinerary])

    subgraph State Persistence
        Postgres[(PostgreSQL Checkpointer)] <--> FlightAgent
        Postgres <--> HotelAgent
        Postgres <--> WeatherAgent
        Postgres <--> ItineraryAgent
    end
```

---

## 🔌 MCP Tools Breakdown

| Server | Transport | Tool Name | Description |
| :--- | :--- | :--- | :--- |
| **Tavily MCP** | `streamable_http` | `tavily_search` | Real-time web search for hotel listings and local attractions. |
| **AviationStack MCP** | `stdio` | `list_airports` | Resolves departure/arrival airport codes and details. |
| **AviationStack MCP** | `stdio` | `list_airlines` | Queries active airline carriers for flight route planning. |
| **Custom Weather MCP** | `stdio` | `get_current_weather` | Retrieves live temperature, wind speed, and weather condition. |
| **Custom Weather MCP** | `stdio` | `get_forecast` | Fetches 5-period weather forecast data for destination city. |

---

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.10+**
- **Docker Desktop** & **Docker Compose**
- API Keys for external services:
  - **Groq API Key**: [console.groq.com](https://console.groq.com)
  - **Tavily API Key**: [tavily.com](https://www.tavily.com/)
  - **AviationStack API Key**: [aviationstack.com](https://aviationstack.com/)
  - **OpenWeatherMap API Key**: [openweathermap.org](https://openweathermap.org/)

---

## 🚀 Quickstart Guide

### 1. Clone the Repository

```bash
git clone https://github.com/Pradumnasaraf/AI-Trip-Planner-MCP.git
cd AI-Trip-Planner-MCP
```

> **Note**: Make sure to also clone or initialize the `aviationstack-mcp` repository inside the project folder:
> ```bash
> git clone https://github.com/Pradumnasaraf/aviationstack-mcp.git
> ```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows (Command Prompt)
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (you can base it on `example.env`):

```bash
cp example.env .env
```

Fill in your API keys and database configuration in `.env`:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key
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

## 🐳 Running Database with Docker

Start PostgreSQL in detached mode using Docker Compose:

```bash
docker compose up -d
```

Verify that the database container is running:

```bash
docker compose ps
```

To stop the database container when finished:

```bash
docker compose down
```

---

## 🏃 Running the Application

Ensure the Docker PostgreSQL container is active, then execute:

```bash
python main.py
```

### Workflow Execution Flow:

1. You will be prompted: `Enter travel requests:`
2. Enter your travel query, e.g.:
   > *"Plan a 5-day trip to Tokyo from Sydney next month."*
3. The graph executes all agent nodes step-by-step:
   - Queries airport & airline lists via **AviationStack MCP**
   - Fetches hotel recommendations via **Tavily MCP**
   - Retrieves live weather & forecast via **Custom Weather MCP**
   - Synthesizes and outputs the final complete travel plan
4. The workflow graph visualization will be saved as `graph.png`.

---

## 🧪 Testing Individual MCP Servers

You can test individual MCP servers using the included test scripts:

- **Test Weather MCP Server**:
  ```bash
  python testing_weather_mcp.py
  ```

- **Test AviationStack MCP Server**:
  ```bash
  python testing_aviationstack_mcp_server.py
  ```

---

## 📂 Project Structure

```
├── main.py                             # Main LangGraph application entrypoint & state graph definition
├── mcp_client.py                       # MultiServerMCPClient manager for Tavily, AviationStack & Weather MCP
├── custom_weather_mcp_server.py        # FastMCP server integrating OpenWeatherMap API
├── testing_weather_mcp.py             # Script to verify weather MCP tools
├── testing_aviationstack_mcp_server.py # Script to verify flight/airport MCP tools
├── docker-compose.yml                  # PostgreSQL container definition for session checkpointing
├── requirements.txt                    # Project Python dependencies
├── example.env                         # Template environment variables configuration
├── graph.png                           # Generated LangGraph visual workflow diagram
└── aviationstack-mcp/                  # AviationStack MCP server integration package
```

---

## 🛠️ Troubleshooting

- **Database Connection Refused**: Make sure Docker Desktop is running and execute `docker compose up -d`. Check that `POSTGRES_PORT` in your `.env` matches the port mapped in `docker-compose.yml` (default `5433`).
- **MCP Server Launch Failure**: Ensure the virtual environment Python path in `mcp_client.py` exists and is functional.
- **Missing API Keys**: Verify `.env` file exists in the root directory and valid keys are provided for Groq, Tavily, AviationStack, and OpenWeatherMap.

---

## 📄 License

This project is open-source. See repository details for license information.
