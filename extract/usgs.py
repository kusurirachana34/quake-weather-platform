import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def fetch_earthquakes(days=1, min_magnitude=2.5, max_retries=4):
    """Ask the USGS API for recent earthquakes, retrying on temporary errors."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    params = {
        "format": "geojson",
        "starttime": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "minmagnitude": min_magnitude,
        "orderby": "time",
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(USGS_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as error:
            status = getattr(error.response, "status_code", None)
            is_client_error = status is not None and status < 500
            # Our own mistakes (4xx) won't fix themselves, so don't retry those
            if is_client_error or attempt == max_retries:
                raise
            wait = 2**attempt
            print(f"Attempt {attempt} failed ({error}). Retrying in {wait}s...")
            time.sleep(wait)


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
