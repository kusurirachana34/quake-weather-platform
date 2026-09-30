import time

import requests


def get_json_with_retry(url, params, max_retries=4, timeout=30):
    """GET a URL and return JSON, retrying on temporary server errors."""
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as error:
            status = getattr(error.response, "status_code", None)
            is_client_error = status is not None and status < 500
            if is_client_error or attempt == max_retries:
                raise
            wait = 2**attempt
            print(f"Attempt {attempt} failed ({error}). Retrying in {wait}s...")
            time.sleep(wait)
