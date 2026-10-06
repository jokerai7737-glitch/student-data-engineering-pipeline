from __future__ import annotations

import pandas as pd


def integrate_data(
    csv_df: pd.DataFrame,
    api_df: pd.DataFrame,
    db_df: pd.DataFrame,
    mongodb_df: pd.DataFrame,
    html_df: pd.DataFrame,
) -> pd.DataFrame:
    """Integrate all five sources using student_id.

    CSV/API/MongoDB/HTML are one-record-per-student sources after validation;
    database is one-to-many because a student can be enrolled in multiple courses.
    """
    merged = csv_df.merge(api_df, on="student_id", how="inner", validate="one_to_one")
    merged = merged.merge(
        mongodb_df,
        on="student_id",
        how="inner",
        validate="one_to_one",
    )
    merged = merged.merge(
        html_df,
        on="student_id",
        how="inner",
        validate="one_to_one",
    )
    integrated = merged.merge(
        db_df,
        on="student_id",
        how="inner",
        validate="one_to_many",
    )
    integrated["source"] = "CSV+API+DATABASE+MONGODB+HTML"
    return integrated
