from __future__ import annotations

import os

from pymongo import MongoClient


URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017")
DATABASE = os.getenv("MONGODB_DATABASE", "student_pipeline")
COLLECTION = os.getenv("MONGODB_COLLECTION", "student_profiles")


# Intentionally imperfect records are inserted into MongoDB so the ETL
# pipeline has realistic quality problems to detect and reject.
MONGODB_DOCUMENTS = [
    {
        "student_id": 1001,
        "email": "ahmed.ali@example.com",
        "phone": "771234567",
        "scholarship_status": "None",
    },
    {
        "student_id": 1002,
        "email": "sara.mohammed@example.com",
        "phone": "772345678",
        "scholarship_status": "Eligible",
    },
    {
        "student_id": 1003,
        "email": "omar.hassan@example.com",
        "phone": "773456789",
        "scholarship_status": "None",
    },
    {
        "student_id": 1004,
        "email": None,
        "phone": "774567890",
        "scholarship_status": "Eligible",
    },
    {
        "student_id": 1005,
        "email": "yousef_at_example.com",
        "phone": "775678901",
        "scholarship_status": "Eligible",
    },
    {
        "student_id": 1006,
        "email": "maryam.ahmed@example.com",
        "phone": "12345",
        "scholarship_status": "None",
    },
    {
        "student_id": 1008,
        "email": "noura.ali@example.com",
        "phone": " 776789012 ",
        "scholarship_status": " active ",
    },
    {
        "student_id": 1009,
        "email": "fahad.musa@example.com",
        "phone": "777890123",
        "scholarship_status": "None",
    },
    {
        "student_id": 1009,
        "email": "fahad.duplicate@example.com",
        "phone": "777890123",
        "scholarship_status": "None",
    },
    {
        "student_id": 1010,
        "email": "huda.salem@example.com",
        "phone": None,
        "scholarship_status": "None",
    },
    {
        "student_id": 1011,
        "email": "ali.nasser@example.com",
        "phone": "778901234",
        "scholarship_status": "Eligible",
    },
    {
        "student_id": 1012,
        "email": "rawan.saleh@example.com",
        "phone": "779012345",
        "scholarship_status": "None",
    },
    {
        "student_id": 9998,
        "email": "extra.profile@example.com",
        "phone": "771111111",
        "scholarship_status": "None",
    },
]


def seed_mongodb() -> None:
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        collection = client[DATABASE][COLLECTION]
        collection.delete_many({})
        result = collection.insert_many(MONGODB_DOCUMENTS)
        print(
            f"Seeded {len(result.inserted_ids)} documents into "
            f"{DATABASE}.{COLLECTION}"
        )
    finally:
        client.close()


if __name__ == "__main__":
    seed_mongodb()
