from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "students.db"

COURSES = [
    (101, "Python Programming", 3),
    (102, "Data Engineering", 3),
    (103, "Artificial Intelligence", 4),
    (104, "Database Systems", 3),
]

ENROLLMENTS = [
    (1001, 101, "2026-S1", 88),
    (1001, 102, "2026-S1", 91),
    (1002, 101, "2026-S1", 79),
    (1003, 103, "2026-S1", 94),
    (1004, 104, "2026-S1", 85),
    (1005, 101, "2026-S1", 110),
    (1006, 102, "2026-S1", 76),
    (1008, 102, "2026-S1", 68),
    (1009, 103, "2026-S1", 82),
    (1010, 104, "2026-S1", 73),
    (1011, 101, "2026-S1", 95),
    (1012, 103, "2026-S1", 87),
    (1012, 104, "2026-S1", 89),
    (None, 101, "2026-S1", 80),
]


def create_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DROP TABLE IF EXISTS enrollments")
        conn.execute("DROP TABLE IF EXISTS courses")
        conn.execute(
            "CREATE TABLE courses (course_id INTEGER PRIMARY KEY, course_name TEXT NOT NULL, credit_hours INTEGER NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE enrollments (student_id INTEGER, course_id INTEGER NOT NULL, semester TEXT NOT NULL, score REAL, FOREIGN KEY(course_id) REFERENCES courses(course_id))"
        )
        conn.executemany("INSERT INTO courses VALUES (?, ?, ?)", COURSES)
        conn.executemany("INSERT INTO enrollments VALUES (?, ?, ?, ?)", ENROLLMENTS)
        conn.commit()


if __name__ == "__main__":
    create_database()
    print(f"Created {DB_PATH}")
