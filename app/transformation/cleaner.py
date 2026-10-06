from __future__ import annotations

import pandas as pd


CITY_MAP = {
    "sanaa": "Sanaa",
    "aden": "Aden",
    "taiz": "Taiz",
    "ibb": "Ibb",
    "hodeidah": "Hodeidah",
}


def clean_students(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    for col in ["student_name", "major", "city"]:
        work[col] = (
            work[col]
            .astype("string")
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
    work["city"] = work["city"].str.lower().map(CITY_MAP).fillna(work["city"].str.title())
    work["major"] = work["major"].str.replace(r"\s+", " ", regex=True)
    work["age"] = pd.to_numeric(work["age"], errors="coerce").astype("Int64")
    return work


def clean_api(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["status"] = (
        work["status"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )
    work["gpa"] = pd.to_numeric(work["gpa"], errors="coerce")
    work["attendance"] = pd.to_numeric(work["attendance"], errors="coerce")
    return work


def clean_database(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["course_name"] = (
        work["course_name"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )
    work["semester"] = work["semester"].astype("string").str.strip().str.upper()
    work["score"] = pd.to_numeric(work["score"], errors="coerce")
    work["credit_hours"] = pd.to_numeric(work["credit_hours"], errors="coerce")
    return work


def clean_mongodb(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["email"] = (
        work["email"].astype("string").str.strip().str.lower()
    )
    work["phone"] = (
        work["phone"].astype("string").str.replace(r"\s+", "", regex=True)
    )
    work["scholarship_status"] = (
        work["scholarship_status"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )
    return work


def clean_html(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["advisor"] = (
        work["advisor"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )
    work["advising_score"] = pd.to_numeric(work["advising_score"], errors="coerce")
    work["academic_warning"] = (
        work["academic_warning"]
        .astype("string")
        .str.strip()
        .str.title()
    )
    return work
