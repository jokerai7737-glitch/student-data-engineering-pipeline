from __future__ import annotations

import pandas as pd


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()

    numeric_cols = [
        "age",
        "gpa",
        "attendance",
        "credit_hours",
        "score",
        "advising_score",
    ]
    for col in numeric_cols:
        work[col] = pd.to_numeric(work[col], errors="coerce")

    # Missing-value strategy: median for numeric measures.
    for col in ["gpa", "attendance", "score", "advising_score"]:
        if work[col].isna().any():
            median = work[col].median()
            if pd.isna(median):
                raise ValueError(f"Cannot impute missing {col}: no usable values available")
            work[col] = work[col].fillna(median)

    # Textual missing values are explicit rather than silently discarded.
    for col in [
        "student_name",
        "major",
        "city",
        "status",
        "email",
        "phone",
        "scholarship_status",
        "advisor",
        "academic_warning",
        "course_name",
        "semester",
    ]:
        work[col] = work[col].fillna("Unknown")

    work["performance_level"] = pd.cut(
        work["gpa"],
        bins=[-float("inf"), 2.0, 2.5, 3.0, 3.5, float("inf")],
        labels=["At Risk", "Acceptable", "Good", "Very Good", "Excellent"],
        right=False,
    ).astype("string")

    work["attendance_status"] = work["attendance"].apply(
        lambda x: "Good" if x >= 75 else "Low"
    )

    work["advising_status"] = work["advising_score"].apply(
        lambda x: "Strong" if x >= 4 else "Needs Review"
    )

    columns = [
        "student_id",
        "student_name",
        "age",
        "major",
        "city",
        "gpa",
        "attendance",
        "status",
        "email",
        "phone",
        "scholarship_status",
        "advisor",
        "advising_score",
        "advising_status",
        "academic_warning",
        "course_id",
        "course_name",
        "credit_hours",
        "semester",
        "score",
        "performance_level",
        "attendance_status",
        "source",
    ]
    return (
        work[columns]
        .sort_values(["student_id", "course_id"])
        .reset_index(drop=True)
    )
