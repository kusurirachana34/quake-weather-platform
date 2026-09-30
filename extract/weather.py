import pandas as pd

from extract.http_utils import get_json_with_retry

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = [
    {"city": "Tokyo", "latitude": 35.68, "longitude": 139.65},
    {"city": "Los Angeles", "latitude": 34.05, "longitude": -118.24},
    {"city": "Santiago", "latitude": -33.45, "longitude": -70.67},
    {"city": "Istanbul", "latitude": 41.01, "longitude": 28.98},
    {"city": "Jakarta", "latitude": -6.21, "longitude": 106.85},
]


def fetch_city_weather(city, past_days=3):
    """Get daily weather for one city (the last few days plus today)."""
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "past_days": past_days,
        "forecast_days": 1,
        "timezone": "UTC",
    }
    data = get_json_with_retry(OPEN_METEO_URL, params)
    daily = data["daily"]
    return pd.DataFrame(
        {
            "city": city["city"],
            "weather_date": pd.to_datetime(daily["time"]).date,
            "temp_max_c": daily["temperature_2m_max"],
            "temp_min_c": daily["temperature_2m_min"],
            "precipitation_mm": daily["precipitation_sum"],
        }
    )


def fetch_all_weather(past_days=3):
    """Get weather for every city in CITIES as one table."""
    frames = [fetch_city_weather(city, past_days) for city in CITIES]
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    df = fetch_all_weather()
    print(f"Fetched {len(df)} weather rows")
    print(df.head(8))
