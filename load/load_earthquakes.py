from sqlalchemy import text

from extract.usgs import fetch_earthquakes, to_dataframe
from load.db import get_engine

CREATE_SCHEMA = "CREATE SCHEMA IF NOT EXISTS raw;"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS raw.earthquakes (
    event_id    TEXT PRIMARY KEY,
    event_time  TIMESTAMPTZ NOT NULL,
    magnitude   DOUBLE PRECISION,
    place       TEXT,
    longitude   DOUBLE PRECISION,
    latitude    DOUBLE PRECISION,
    depth_km    DOUBLE PRECISION,
    event_type  TEXT,
    loaded_at   TIMESTAMPTZ DEFAULT NOW()
);
"""

UPSERT = """
INSERT INTO raw.earthquakes
    (event_id, event_time, magnitude, place, longitude, latitude, depth_km, event_type)
VALUES
    (:event_id, :event_time, :magnitude, :place, :longitude, :latitude, :depth_km, :event_type)
ON CONFLICT (event_id) DO UPDATE SET
    magnitude = EXCLUDED.magnitude,
    place     = EXCLUDED.place,
    depth_km  = EXCLUDED.depth_km,
    loaded_at = NOW();
"""


def load_earthquakes(df):
    """Save earthquakes into PostgreSQL. Safe to run many times."""
    if df.empty:
        print("No earthquakes to load.")
        return 0

    df = df.rename(columns={"time": "event_time"})
    # Turn missing values (NaN) into real NULLs for the database
    df = df.astype(object).where(df.notna(), None)
    records = df.to_dict("records")

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(CREATE_SCHEMA))
        conn.execute(text(CREATE_TABLE))
        conn.execute(text(UPSERT), records)

    return len(records)


if __name__ == "__main__":
    data = fetch_earthquakes()
    df = to_dataframe(data)
    count = load_earthquakes(df)
    print(f"Loaded {count} earthquakes into raw.earthquakes")
