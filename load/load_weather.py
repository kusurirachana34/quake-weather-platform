from sqlalchemy import text

from extract.weather import fetch_all_weather
from load.db import get_engine

CREATE_SCHEMA = "CREATE SCHEMA IF NOT EXISTS raw;"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS raw.weather_daily (
    city              TEXT NOT NULL,
    weather_date      DATE NOT NULL,
    temp_max_c        DOUBLE PRECISION,
    temp_min_c        DOUBLE PRECISION,
    precipitation_mm  DOUBLE PRECISION,
    loaded_at         TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (city, weather_date)
);
"""

UPSERT = """
INSERT INTO raw.weather_daily
    (city, weather_date, temp_max_c, temp_min_c, precipitation_mm)
VALUES
    (:city, :weather_date, :temp_max_c, :temp_min_c, :precipitation_mm)
ON CONFLICT (city, weather_date) DO UPDATE SET
    temp_max_c       = EXCLUDED.temp_max_c,
    temp_min_c       = EXCLUDED.temp_min_c,
    precipitation_mm = EXCLUDED.precipitation_mm,
    loaded_at        = NOW();
"""


def load_weather(df):
    """Save weather rows into PostgreSQL. Safe to run many times."""
    if df.empty:
        print("No weather rows to load.")
        return 0

    df = df.astype(object).where(df.notna(), None)
    records = df.to_dict("records")

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(CREATE_SCHEMA))
        conn.execute(text(CREATE_TABLE))
        conn.execute(text(UPSERT), records)

    return len(records)


if __name__ == "__main__":
    df = fetch_all_weather()
    count = load_weather(df)
    print(f"Loaded {count} rows into raw.weather_daily")
