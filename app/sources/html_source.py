from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd
import requests


REQUIRED_COLUMNS = [
    "student_id",
    "advisor",
    "advising_score",
    "academic_warning",
]


def _read_html_content(source: str | Path, timeout: int = 10) -> str:
    text = str(source)
    if text.lower().startswith(("http://", "https://")):
        try:
            response = requests.get(text, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"HTML request failed: {exc}") from exc
        return response.text

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"HTML source not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_html(source: str | Path, timeout: int = 10) -> pd.DataFrame:
    """Extract the first HTML table containing the required student columns."""
    content = _read_html_content(source, timeout=timeout)
    try:
        tables: list[pd.DataFrame] = pd.read_html(StringIO(content))
    except ValueError as exc:
        raise RuntimeError("HTML page does not contain a readable table") from exc

    for df in tables:
        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if not missing:
            return df[REQUIRED_COLUMNS].copy()

    raise ValueError(
        "HTML page does not contain a table with required columns: "
        f"{REQUIRED_COLUMNS}"
    )
