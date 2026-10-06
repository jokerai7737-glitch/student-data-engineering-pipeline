from __future__ import annotations

from dataclasses import dataclass
import json
import pandas as pd


@dataclass
class ValidationResult:
    valid: pd.DataFrame
    rejected: pd.DataFrame


def _normalize_student_id(series: pd.Series) -> pd.Series:
    """Normalize student IDs across all heterogeneous sources."""
    numeric = pd.to_numeric(series, errors="coerce")
    normalized = series.astype("string").str.strip()
    whole_numeric = numeric.notna() & (numeric % 1 == 0)
    normalized.loc[whole_numeric] = numeric.loc[whole_numeric].astype("Int64").astype("string")
    return normalized


def _rejection_rows(
    df: pd.DataFrame, mask: pd.Series, source: str, reason: str
) -> pd.DataFrame:
    if not mask.any():
        return pd.DataFrame(columns=["source", "student_id", "error_reason", "record_data"])
    rows = df.loc[mask].copy()
    rows["source"] = source
    rows["error_reason"] = reason
    rows["record_data"] = rows.astype(str).to_dict(orient="records")
    rows["record_data"] = rows["record_data"].map(json.dumps)
    rows["student_id"] = _normalize_student_id(rows["student_id"])
    return rows[["source", "student_id", "error_reason", "record_data"]]


def validate_students(df: pd.DataFrame) -> ValidationResult:
    work = df.copy()
    work["student_id"] = _normalize_student_id(work["student_id"])

    missing_mask = work["student_id"].isna() | (work["student_id"] == "")
    duplicate_mask = work["student_id"].notna() & work["student_id"].duplicated(keep="first")
    numeric_age = pd.to_numeric(work["age"], errors="coerce")
    invalid_age = numeric_age.notna() & ~numeric_age.between(16, 80)

    rejection_frames = [
        _rejection_rows(work, missing_mask, "CSV", "Missing student_id"),
        _rejection_rows(work, duplicate_mask, "CSV", "Duplicate student_id"),
        _rejection_rows(work, invalid_age, "CSV", "Invalid Age"),
    ]

    invalid_row_mask = missing_mask | duplicate_mask | invalid_age
    valid = work.loc[~invalid_row_mask].copy()
    valid["age"] = numeric_age.loc[valid.index].astype("Int64")
    rejected = (
        pd.concat([p for p in rejection_frames if not p.empty], ignore_index=True)
        if any(not p.empty for p in rejection_frames)
        else pd.DataFrame()
    )
    return ValidationResult(valid=valid, rejected=rejected)


def validate_api(df: pd.DataFrame) -> ValidationResult:
    work = df.copy()
    work["student_id"] = _normalize_student_id(work["student_id"])

    missing_mask = work["student_id"].isna() | (work["student_id"] == "")
    duplicate_mask = work["student_id"].notna() & work["student_id"].duplicated(keep="first")
    gpa = pd.to_numeric(work["gpa"], errors="coerce")
    attendance = pd.to_numeric(work["attendance"], errors="coerce")
    invalid_gpa = gpa.notna() & ~gpa.between(0, 4)
    invalid_att = attendance.notna() & ~attendance.between(0, 100)

    rejection_frames = [
        _rejection_rows(work, missing_mask, "API", "Missing student_id"),
        _rejection_rows(work, duplicate_mask, "API", "Duplicate student_id"),
        _rejection_rows(work, invalid_gpa, "API", "Invalid GPA"),
        _rejection_rows(work, invalid_att, "API", "Invalid Attendance"),
    ]

    invalid_row_mask = missing_mask | duplicate_mask | invalid_gpa | invalid_att
    valid = work.loc[~invalid_row_mask].copy()
    valid["gpa"] = gpa.loc[valid.index]
    valid["attendance"] = attendance.loc[valid.index]
    rejected = (
        pd.concat([p for p in rejection_frames if not p.empty], ignore_index=True)
        if any(not p.empty for p in rejection_frames)
        else pd.DataFrame()
    )
    return ValidationResult(valid=valid, rejected=rejected)


def validate_database(df: pd.DataFrame) -> ValidationResult:
    work = df.copy()
    work["student_id"] = _normalize_student_id(work["student_id"])
    rejected_parts = [
        _rejection_rows(
            work,
            work["student_id"].isna() | (work["student_id"] == ""),
            "DATABASE",
            "Missing student_id",
        )
    ]

    score = pd.to_numeric(work["score"], errors="coerce")
    invalid_score = score.notna() & ~score.between(0, 100)
    rejected_parts.append(_rejection_rows(work, invalid_score, "DATABASE", "Invalid Score"))

    missing_course = work["course_name"].isna()
    rejected_parts.append(
        _rejection_rows(work, missing_course, "DATABASE", "Unknown course_id")
    )

    invalid_rows = pd.Series(False, index=work.index)
    for part in rejected_parts:
        if not part.empty:
            invalid_rows.loc[part.index] = True

    valid = work.loc[~invalid_rows].copy()
    valid["score"] = score.loc[valid.index]
    rejected = (
        pd.concat([p for p in rejected_parts if not p.empty], ignore_index=True)
        if any(not p.empty for p in rejected_parts)
        else pd.DataFrame()
    )
    return ValidationResult(valid=valid, rejected=rejected)


def validate_mongodb(df: pd.DataFrame) -> ValidationResult:
    work = df.copy()
    work["student_id"] = _normalize_student_id(work["student_id"])

    missing_mask = work["student_id"].isna() | (work["student_id"] == "")
    duplicate_mask = work["student_id"].notna() & work["student_id"].duplicated(keep="first")
    email = work["email"].astype("string").str.strip()
    invalid_email = email.notna() & (email != "") & ~email.str.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$", na=False
    )
    phone = work["phone"].astype("string").str.replace(r"\s+", "", regex=True)
    invalid_phone = phone.notna() & (phone != "") & ~phone.str.match(
        r"^7\d{8}$", na=False
    )

    rejection_frames = [
        _rejection_rows(work, missing_mask, "MONGODB", "Missing student_id"),
        _rejection_rows(work, duplicate_mask, "MONGODB", "Duplicate student_id"),
        _rejection_rows(work, invalid_email, "MONGODB", "Invalid Email"),
        _rejection_rows(work, invalid_phone, "MONGODB", "Invalid Phone"),
    ]

    invalid_row_mask = missing_mask | duplicate_mask | invalid_email | invalid_phone
    valid = work.loc[~invalid_row_mask].copy()
    valid["email"] = email.loc[valid.index]
    valid["phone"] = phone.loc[valid.index]
    rejected = (
        pd.concat([p for p in rejection_frames if not p.empty], ignore_index=True)
        if any(not p.empty for p in rejection_frames)
        else pd.DataFrame()
    )
    return ValidationResult(valid=valid, rejected=rejected)


def validate_html(df: pd.DataFrame) -> ValidationResult:
    work = df.copy()
    work["student_id"] = _normalize_student_id(work["student_id"])

    missing_mask = work["student_id"].isna() | (work["student_id"] == "")
    duplicate_mask = work["student_id"].notna() & work["student_id"].duplicated(keep="first")
    advising_score = pd.to_numeric(work["advising_score"], errors="coerce")
    invalid_advising_score = advising_score.notna() & ~advising_score.between(0, 5)

    rejection_frames = [
        _rejection_rows(work, missing_mask, "HTML", "Missing student_id"),
        _rejection_rows(work, duplicate_mask, "HTML", "Duplicate student_id"),
        _rejection_rows(work, invalid_advising_score, "HTML", "Invalid Advising Score"),
    ]

    invalid_row_mask = missing_mask | duplicate_mask | invalid_advising_score
    valid = work.loc[~invalid_row_mask].copy()
    valid["advising_score"] = advising_score.loc[valid.index]
    rejected = (
        pd.concat([p for p in rejection_frames if not p.empty], ignore_index=True)
        if any(not p.empty for p in rejection_frames)
        else pd.DataFrame()
    )
    return ValidationResult(valid=valid, rejected=rejected)


def validate_final(df: pd.DataFrame) -> ValidationResult:
    work = df.copy()
    checks = [
        work["student_id"].isna() | (work["student_id"].astype(str).str.strip() == ""),
        ~pd.to_numeric(work["age"], errors="coerce").between(16, 80),
        ~pd.to_numeric(work["gpa"], errors="coerce").between(0, 4),
        ~pd.to_numeric(work["attendance"], errors="coerce").between(0, 100),
        ~pd.to_numeric(work["score"], errors="coerce").between(0, 100),
        ~pd.to_numeric(work["advising_score"], errors="coerce").between(0, 5),
    ]
    reason_names = [
        "Missing student_id",
        "Invalid Age",
        "Invalid GPA",
        "Invalid Attendance",
        "Invalid Score",
        "Invalid Advising Score",
    ]

    invalid_any = pd.Series(False, index=work.index)
    reasons = pd.Series("", index=work.index, dtype="string")
    for mask, reason in zip(checks, reason_names):
        mask = mask.fillna(True)
        invalid_any |= mask
        reasons = reasons.mask(mask & (reasons == ""), reason)

    if invalid_any.any():
        bad = work.loc[invalid_any].copy()
        bad["source"] = "FINAL"
        bad["student_id"] = _normalize_student_id(bad["student_id"])
        bad["error_reason"] = reasons.loc[bad.index]
        bad["record_data"] = bad.astype(str).to_dict(orient="records")
        bad["record_data"] = bad["record_data"].map(json.dumps)
        rejected = bad[["source", "student_id", "error_reason", "record_data"]]
    else:
        rejected = pd.DataFrame(
            columns=["source", "student_id", "error_reason", "record_data"]
        )

    valid = work.loc[~invalid_any].copy()
    return ValidationResult(valid=valid, rejected=rejected)
