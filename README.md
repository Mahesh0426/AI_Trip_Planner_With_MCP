# AI Trip Planner with MCP

AI Trip Planner is a Python-based application for generating travel itineraries using AI models, API integrations, and persistent checkpoints via PostgreSQL.

The project uses Model-Chain Protocol (MCP) concepts with tools like LangChain, LangGraph, Groq, and PostgreSQL for stateful trip planning.

## Key Features

- AI-assisted trip planning and itinerary generation
- External travel and aviation API integration
- PostgreSQL checkpointing for session persistence
- Docker-based database setup for local development

## Prerequisites

- Python 3.10 or newer
- Docker & Docker Desktop
- A Python virtual environment (recommended)

## Setup

1. Clone the repository and change into the project folder:

   ```bash
   cd /path/to/AI-Trip-Planner-MCP
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

Create a `.env` file at the project root with the following values:

```env
COHERE_API_KEY=your_cohere_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_KEY=your_groq_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key

# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=trip_planner
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/trip_planner
```

> Tip: If you are using a different database host or credentials, update `DATABASE_URL` accordingly.

## API Dependencies

This application may use the following APIs:

- Groq API: https://console.groq.com
- Tavily API: https://www.tavily.com/
- AviationStack API: https://aviationstack.com/
- OpenWeatherMap API: https://openweathermap.org/

## Running PostgreSQL with Docker

Start the local Postgres container from the project directory:

```bash
docker compose up -d
```

Verify the container is running:

```bash
docker compose ps
```

To stop the database container:

```bash
docker compose down
```

## Running the Application

Once dependencies are installed and the database is running, start the app:

```bash
python main.py
```

## Troubleshooting

- Ensure Docker Desktop is running before starting the database.
- Verify the `.env` values are correct and that `DATABASE_URL` matches your Docker Postgres settings.
- If you change environment variables, restart the application after updating `.env`.

## Notes

- The project assumes a local PostgreSQL instance running on `localhost:5432`.
- Data persistence is handled by the Docker volume named `postgres_data`.

## License

This repository does not include a license file by default. Add one if you want to share or publish the project.
