from __future__ import annotations

from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = ["student_id", "student_name", "age", "major", "city"]


def extract_csv(path: str | Path) -> pd.DataFrame:
    """Extract raw student data from a CSV file."""
    df = pd.read_csv(path, dtype={"student_id": "string"})
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    return df[REQUIRED_COLUMNS].copy()
