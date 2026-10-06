from __future__ import annotations

from typing import Any
import requests
import pandas as pd


REQUIRED_COLUMNS = ["student_id", "gpa", "attendance", "status"]


def extract_api(url: str, timeout: int = 5) -> pd.DataFrame:
    """Extract JSON records from a REST endpoint with explicit error handling."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("API timeout") from exc
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError("API connection error") from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"API HTTP error: {response.status_code}") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"API request error: {exc}") from exc

    try:
        payload: Any = response.json()
    except ValueError as exc:
        raise RuntimeError("API returned invalid JSON") from exc

    if not payload:
        raise RuntimeError("API returned an empty response")

    if isinstance(payload, dict) and "data" in payload:
        payload = payload["data"]
    if not isinstance(payload, list):
        raise RuntimeError("API JSON must contain a list of records")

    df = pd.DataFrame(payload)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"API missing required columns: {missing}")
    return df[REQUIRED_COLUMNS].copy()
