from __future__ import annotations

from pathlib import Path
import pandas as pd


def save_csv(df: pd.DataFrame, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8-sig")


def append_rejections(df: pd.DataFrame, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        return
    if out.exists():
        existing = pd.read_csv(out, dtype={"student_id": "string"})
        combined = pd.concat([existing, df], ignore_index=True)
    else:
        combined = df.copy()
    combined.to_csv(out, index=False, encoding="utf-8-sig")
