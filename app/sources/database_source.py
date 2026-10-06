from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd


REQUIRED_COLUMNS = [
    "student_id", "course_id", "course_name", "credit_hours", "semester", "score"
]


def extract_database(path: str | Path) -> pd.DataFrame:
    """Extract enrollment/course data from SQLite using a SQL JOIN."""
    query = """
        SELECT
            e.student_id,
            e.course_id,
            c.course_name,
            c.credit_hours,
            e.semester,
            e.score
        FROM enrollments e
        LEFT JOIN courses c ON e.course_id = c.course_id
        ORDER BY e.student_id, e.course_id;
    """
    conn = sqlite3.connect(path)
    try:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Database result missing columns: {missing}")
    return df[REQUIRED_COLUMNS].copy()
