# Quake & Weather Data Platform

An automated data pipeline that collects earthquake and weather data from
public APIs, stores it in PostgreSQL, and prepares it for analysis.

## Data sources
- **USGS Earthquake API**: recent earthquakes worldwide
- **Open-Meteo API**: daily weather for selected cities

## Tech stack
Python, pandas, SQLAlchemy, PostgreSQL, Docker Compose, Git

## How it works
1. **Extract:** Python calls each API, retrying on temporary server errors
2. **Load:** data is upserted into the `raw` schema in PostgreSQL, so reruns never create duplicates

## Run it locally

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env    # then set your own password in .env
    docker compose up -d
    python -m load.load_earthquakes
    python -m load.load_weather

## Status
In progress: dbt transformations, data quality tests, Airflow scheduling.