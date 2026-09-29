import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def fetch_earthquakes(days=1, min_magnitude=2.5):
    """Ask the USGS API for earthquakes from the last `days` days."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    params = {
        "format": "geojson",
        "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "minmagnitude": min_magnitude,
        "orderby": "time",
    }

    response = requests.get(USGS_URL, params=params, timeout=30)
    response.raise_for_status()  # stops with an error if the request failed
    return response.json()


def to_dataframe(data):
    """Turn the raw API answer into a table with one row per earthquake."""
    rows = []
    for feature in data["features"]:
        props = feature["properties"]
        lon, lat, depth = feature["geometry"]["coordinates"]
        rows.append(
            {
                "event_id": feature["id"],
                "time": pd.to_datetime(props["time"], unit="ms", utc=True),
                "magnitude": props["mag"],
                "place": props["place"],
                "longitude": lon,
                "latitude": lat,
                "depth_km": depth,
                "event_type": props["type"],
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    data = fetch_earthquakes()
    df = to_dataframe(data)
    print(f"Fetched {len(df)} earthquakes")
    print(df.head())