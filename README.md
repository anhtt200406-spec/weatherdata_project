# Weather Data Pipeline

An ELT pipeline that collects real-time weather data for Hanoi from the [Weatherstack API](https://weatherstack.com), stores it in PostgreSQL, orchestrates ingestion with Apache Airflow, and transforms it with dbt.

## Architecture

```
Weatherstack API
      │
      ▼
api_request.py       ← fetch JSON payload
      │
      ▼
insert_record.py     ← parse & INSERT into PostgreSQL
      │
      ▼
PostgreSQL           ← weather_schema.weather_data
      │
      ▼
dbt (transform)      ← staging → mart models
```

Airflow schedules the fetch → insert step every **1 minute**.

## Stack

| Component | Technology |
|-----------|-----------|
| Ingestion | Python + Requests |
| Database  | PostgreSQL 14 |
| Orchestration | Apache Airflow |
| Transformation | dbt-postgres 1.9 |
| Infrastructure | Docker Compose |

## dbt Models

```
models/
├── sources/          raw source definition (weather_schema.weather_data)
├── staging/
│   └── stg_weather_data     deduplicated records (partition by timestamp)
└── mart/
    ├── daily_average        avg temperature / wind speed / humidity
    └── weather_report       full report view
```

dbt tests cover: valid temperature & humidity ranges, non-negative wind speed, no duplicate timestamps, and row count consistency.

## Getting Started

**Prerequisites:** Docker, Docker Compose, a Weatherstack API key.

```bash
# 1. Clone and configure environment
cp .env.example .env
# Edit .env with your credentials and API key

# 2. Start all services
docker-compose up

# Airflow UI → http://localhost:8080
# Enable the `weather-api-orchestrator` DAG
```

**Run dbt manually:**
```bash
docker-compose run dbt run
docker-compose run dbt test
```

**Run locally (without Docker):**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python api_request/insert_record.py
```

## Project Structure

```
├── api_request/          Python scripts for API fetch & DB insert
├── airflow/dags/         Airflow DAG + task scripts (runs inside container)
├── dbt/my_project/       dbt project (models, tests, profiles)
├── postgres/             PostgreSQL init SQL & Docker volume mount
├── tests/                Unit & integration tests (pytest)
├── docker-compose.yaml
├── .env.example          Environment variable template
└── requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_DB` | Database name |
| `POSTGRES_HOST` | Host (`localhost` for local, `db` inside Docker) |
| `AIRFLOW_DB_CONN` | Airflow SQLAlchemy connection string |
| `WEATHER_API_KEY` | Weatherstack API key |
