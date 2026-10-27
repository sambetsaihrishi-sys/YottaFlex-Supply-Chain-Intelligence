import subprocess
import sys
import time


PIPELINE = [
    ("Generate Master and Transaction Data", "src.data_generator"),
    ("Generate Production Data", "src.production_engine"),
    ("Calculate Projected Inventory", "src.inventory_engine"),
    ("Detect Shortages", "src.shortage_engine"),
    ("Generate Mitigations", "src.mitigation_engine"),
    ("Validate Production", "src.production_validation"),
    ("Allocate Supplier Capacity", "src.capacity_allocator"),
    ("Validate Supplier Allocations", "src.allocation_validation"),
    ("Allocate Production Materials", "src.material_allocator"),
    ("Generate Anomaly Cases", "src.anomaly_generator"),
    ("Detect Anomalies", "src.anomaly_detector"),
    ("Evaluate Anomalies", "src.anomaly_evaluation"),
    ("Generate Evaluation Test Cases", "src.anomaly_test_cases"),
    ("Detect Evaluation Cases", "src.evaluation_detector"),
    ("Calculate Evaluation Metrics", "src.evaluation_metrics"),
]


def run_module(name, module):
    print(f"\n{'=' * 60}")
    print(f"RUNNING: {name}")
    print(f"{'=' * 60}")

    start = time.perf_counter()

    result = subprocess.run(
        [sys.executable, "-m", module],
        check=False
    )

    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        raise RuntimeError(
            f"{name} failed with exit code {result.returncode}"
        )

    print(f"PASS: {name}")
    print(f"Execution time: {elapsed:.2f} seconds")


def main():
    print("\nYOTTAFLEX SUPPLY CHAIN PIPELINE")

    for name, module in PIPELINE:
        run_module(name, module)

    print("\nRunning automated tests...")

    subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        check=True
    )

    print("\nPipeline completed successfully!")
    print("Review validation reports before submission.")


if __name__ == "__main__":
    main()