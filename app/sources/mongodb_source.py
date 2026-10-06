from __future__ import annotations

from typing import Any

import pandas as pd


REQUIRED_COLUMNS = [
    "student_id",
    "email",
    "phone",
    "scholarship_status",
]


def extract_mongodb(
    uri: str,
    database: str,
    collection: str,
    *,
    timeout_ms: int = 5000,
) -> pd.DataFrame:
    """Extract student profiles directly from a real MongoDB collection.

    MongoDB is the actual source of truth for this input. No JSON seed file is
    read by the pipeline. The collection is populated separately by
    ``database/init_mongodb.py``.
    """
    try:
        from pymongo import MongoClient
    except ImportError as exc:
        raise RuntimeError(
            "pymongo is required for MongoDB extraction. Install requirements.txt."
        ) from exc

    client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
    try:
        client.admin.command("ping")
        rows: list[dict[str, Any]] = list(
            client[database][collection].find({}, {"_id": 0})
        )
    except Exception as exc:
        raise RuntimeError(
            f"MongoDB extraction failed for {database}.{collection}: {exc}"
        ) from exc
    finally:
        client.close()

    if not rows:
        raise RuntimeError(
            f"MongoDB collection {database}.{collection} returned no documents"
        )

    df = pd.DataFrame(rows)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"MongoDB missing required columns: {missing}")
    return df[REQUIRED_COLUMNS].copy()
