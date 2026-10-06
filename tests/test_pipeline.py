from __future__ import annotations

import unittest
from pathlib import Path

from app.mock_api import start_mock_api
from app.pipeline import run_pipeline
from app.sources.api_source import extract_api
from app.sources.csv_source import extract_csv
from app.sources.database_source import extract_database
from app.sources.mongodb_source import extract_mongodb
from app.sources.html_source import extract_html


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config.json"


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The assignment intentionally uses a real MongoDB source. Tests that
        # require the full pipeline are skipped when MongoDB is not running.
        try:
            from pymongo import MongoClient
            client = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=1000)
            client.admin.command("ping")
            client.close()
        except Exception as exc:
            raise unittest.SkipTest(
                "MongoDB is not running on mongodb://127.0.0.1:27017; "
                "run database/init_mongodb.py after starting MongoDB."
            ) from exc

        cls.result = run_pipeline(CONFIG)

    def test_csv_loaded(self):
        self.assertGreater(len(extract_csv(ROOT / "data/raw/students.csv")), 0)

    def test_api_connected(self):
        server, _ = start_mock_api(
            ROOT / "data/raw/api_response.json",
            "127.0.0.1",
            8766,
            "/students",
        )
        try:
            df = extract_api("http://127.0.0.1:8766/students")
            self.assertGreater(len(df), 0)
        finally:
            server.shutdown()
            server.server_close()

    def test_sqlite_extraction(self):
        df = extract_database(ROOT / "database/students.db")
        self.assertIn("course_name", df.columns)
        self.assertGreater(len(df), 0)

    def test_mongodb_extraction_uses_real_collection(self):
        config = __import__("json").loads(CONFIG.read_text(encoding="utf-8"))
        mongo = config["mongodb"]
        df = extract_mongodb(
            mongo["uri"],
            mongo["database"],
            mongo["collection"],
            timeout_ms=int(mongo.get("timeout_ms", 5000)),
        )
        self.assertIn("email", df.columns)
        self.assertGreater(len(df), 0)

    def test_no_mongodb_json_seed_file(self):
        self.assertFalse((ROOT / "data/raw/mongodb_students.json").exists())
        self.assertNotIn("mongodb_json", __import__("json").loads(CONFIG.read_text(encoding="utf-8"))["paths"])

    def test_html_extraction(self):
        df = extract_html(ROOT / "data/raw/student_advising.html")
        self.assertIn("advisor", df.columns)
        self.assertGreater(len(df), 0)

    def test_duplicates_removed_or_rejected(self):
        reasons = set(self.result["rejected"]["error_reason"].astype(str))
        self.assertIn("Duplicate student_id", reasons)

    def test_missing_values_processed(self):
        self.assertEqual(int(self.result["final_dataset"].isna().sum().sum()), 0)

    def test_invalid_records_rejected(self):
        reasons = set(self.result["rejected"]["error_reason"].astype(str))
        required = {
            "Invalid Age",
            "Invalid GPA",
            "Invalid Attendance",
            "Invalid Score",
            "Invalid Email",
            "Invalid Phone",
            "Invalid Advising Score",
        }
        self.assertTrue(required <= reasons)

    def test_incompatible_source_records_rejected(self):
        reasons = set(self.result["rejected"]["error_reason"].astype(str))
        self.assertIn("student_id not compatible with validated CSV source", reasons)

    def test_integration_success(self):
        self.assertGreater(len(self.result["final_dataset"]), 0)
        self.assertIn("student_id", self.result["final_dataset"].columns)
        self.assertIn("course_name", self.result["final_dataset"].columns)
        self.assertIn("email", self.result["final_dataset"].columns)
        self.assertIn("advisor", self.result["final_dataset"].columns)

    def test_new_source_columns_are_cleaned(self):
        final = self.result["final_dataset"]
        self.assertNotIn(None, final["advisor"].tolist())
        self.assertTrue(final["phone"].astype(str).str.match(r"^7\d{8}$|^Unknown$").all())

    def test_final_dataset_created(self):
        path = ROOT / "data/processed/final_dataset.csv"
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
