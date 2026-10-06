from __future__ import annotations

from app.pipeline import run_pipeline


if __name__ == "__main__":
    result = run_pipeline()
    print("\n-----------------------------------")
    print("PIPELINE EXECUTION SUMMARY")
    print("-----------------------------------")
    for key, value in result["metrics"].items():
        print(f"{key:<20}: {value}")
    print("-----------------------------------")
    print("Final dataset : data/processed/final_dataset.csv")
    print("Rejected data : data/rejected/rejected_records.csv")
    print("Log file      : logs/pipeline.log")
