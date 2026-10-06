from __future__ import annotations

import json
from pathlib import Path
import time

import pandas as pd

from app.mock_api import start_mock_api
from app.output.csv_writer import save_csv
from app.sources.api_source import extract_api
from app.sources.csv_source import extract_csv
from app.sources.database_source import extract_database
from app.sources.mongodb_source import extract_mongodb
from app.sources.html_source import extract_html
from app.transformation.cleaner import (
    clean_api,
    clean_database,
    clean_html,
    clean_mongodb,
    clean_students,
)
from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data
from app.validation.quality import (
    validate_api,
    validate_database,
    validate_final,
    validate_html,
    validate_mongodb,
    validate_students,
)
from app.utils.logger import setup_logger


def load_config(path: str | Path = "config.json") -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _reject_extra_ids(
    dataframe: pd.DataFrame,
    allowed_ids: set[str],
    source_name: str,
) -> pd.DataFrame:
    """Return records whose student_id is not compatible with the master CSV source."""
    extra = dataframe[
        ~dataframe["student_id"].astype(str).isin(allowed_ids)
    ].copy()
    if extra.empty:
        return pd.DataFrame(
            columns=["source", "student_id", "error_reason", "record_data"]
        )

    extra["source"] = source_name
    extra["error_reason"] = "student_id not compatible with validated CSV source"
    extra["record_data"] = extra.astype(str).to_dict(orient="records")
    extra["record_data"] = extra["record_data"].map(json.dumps)
    return extra[["source", "student_id", "error_reason", "record_data"]]


def _log_source_coverage(
    logger,
    source_name: str,
    csv_ids: set[str],
    source_df: pd.DataFrame,
) -> None:
    source_ids = set(source_df["student_id"].astype(str))
    missing = csv_ids - source_ids
    extra = source_ids - csv_ids
    if missing:
        logger.warning("CSV student IDs missing from %s: %s", source_name, sorted(missing))
    if extra:
        logger.warning("Extra student IDs found in %s: %s", source_name, sorted(extra))


def run_pipeline(config_path: str | Path = "config.json") -> dict:
    config = load_config(config_path)
    paths = config["paths"]
    logger = setup_logger(paths["log_file"])
    start_time = time.perf_counter()
    rejection_frames = []

    logger.info("Pipeline execution started")

    # 1) Extract
    logger.info("CSV extraction started")
    csv_raw = extract_csv(paths["students_csv"])
    logger.info("CSV records: %s", len(csv_raw))

    logger.info("API extraction started")
    server = None
    try:
        if config["api"].get("use_mock", True):
            server, _ = start_mock_api(
                paths["api_json"],
                config["api"]["host"],
                int(config["api"]["port"]),
                config["api"]["endpoint"],
            )
            url = (
                f"http://{config['api']['host']}:{config['api']['port']}"
                f"{config['api']['endpoint']}"
            )
        else:
            url = config["api"]["url"]
        api_raw = extract_api(url)
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
    logger.info("API records: %s", len(api_raw))

    logger.info("Database extraction started")
    db_raw = extract_database(paths["database"])
    logger.info("Database records: %s", len(db_raw))

    logger.info("MongoDB extraction started")
    mongo_cfg = config["mongodb"]
    mongo_raw = extract_mongodb(
        mongo_cfg.get("uri", "mongodb://127.0.0.1:27017"),
        mongo_cfg["database"],
        mongo_cfg["collection"],
        timeout_ms=int(mongo_cfg.get("timeout_ms", 5000)),
    )
    logger.info("MongoDB records: %s", len(mongo_raw))

    logger.info("HTML extraction started")
    html_cfg = config["html"]
    html_source = html_cfg.get("url") if html_cfg.get("use_url") else paths["html_page"]
    html_raw = extract_html(html_source)
    logger.info("HTML records: %s", len(html_raw))

    # 2) Validate each source
    logger.info("Source validation started")
    csv_v = validate_students(csv_raw)
    api_v = validate_api(api_raw)
    db_v = validate_database(db_raw)
    mongo_v = validate_mongodb(mongo_raw)
    html_v = validate_html(html_raw)
    rejection_frames.extend(
        [csv_v.rejected, api_v.rejected, db_v.rejected, mongo_v.rejected, html_v.rejected]
    )
    logger.info("Source validation completed")

    # 3) Clean
    csv_clean = clean_students(csv_v.valid)
    api_clean = clean_api(api_v.valid)
    db_clean = clean_database(db_v.valid)
    mongo_clean = clean_mongodb(mongo_v.valid)
    html_clean = clean_html(html_v.valid)
    logger.info("Cleaning completed")

    # 4) Compatibility / coverage checks
    csv_ids = set(csv_clean["student_id"].astype(str))
    for source_name, source_df in [
        ("API", api_clean),
        ("DATABASE", db_clean),
        ("MONGODB", mongo_clean),
        ("HTML", html_clean),
    ]:
        _log_source_coverage(logger, source_name, csv_ids, source_df)
        incompatible = _reject_extra_ids(source_df, csv_ids, source_name)
        if not incompatible.empty:
            rejection_frames.append(incompatible)

    # 5) Integrate
    logger.info("Data integration started")
    integrated = integrate_data(
        csv_clean,
        api_clean,
        db_clean,
        mongo_clean,
        html_clean,
    )
    logger.info("Integrated records: %s", len(integrated))

    # 6) Transform
    logger.info("Transformation started")
    transformed = transform_data(integrated)
    final_v = validate_final(transformed)
    rejection_frames.append(final_v.rejected)

    # 7) Load
    save_csv(final_v.valid, paths["final_dataset"])

    rejections = (
        pd.concat(
            [df for df in rejection_frames if not df.empty],
            ignore_index=True,
        )
        if any(not df.empty for df in rejection_frames)
        else pd.DataFrame(
            columns=["source", "student_id", "error_reason", "record_data"]
        )
    )
    rejections = rejections.drop_duplicates(
        subset=["source", "student_id", "error_reason", "record_data"]
    )
    save_csv(rejections, paths["rejected_records"])

    duration = time.perf_counter() - start_time
    metrics = {
        "CSV Records": len(csv_raw),
        "API Records": len(api_raw),
        "Database Records": len(db_raw),
        "MongoDB Records": len(mongo_raw),
        "HTML Records": len(html_raw),
        "Integrated Records": len(integrated),
        "Valid Records": len(final_v.valid),
        "Rejected Records": len(rejections),
        "Duplicate Records": int(
            csv_raw["student_id"].duplicated().sum()
            + api_raw["student_id"].duplicated().sum()
            + mongo_raw["student_id"].duplicated().sum()
            + html_raw["student_id"].duplicated().sum()
        ),
        "Missing Values": int(final_v.valid.isna().sum().sum()),
        "Processing Time": round(duration, 2),
    }

    logger.info("Final dataset created: %s", len(final_v.valid))
    logger.info("Pipeline execution completed in %.2f seconds", duration)
    return {"metrics": metrics, "final_dataset": final_v.valid, "rejected": rejections}
