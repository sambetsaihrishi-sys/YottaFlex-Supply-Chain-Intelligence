import hashlib
import json
import subprocess
import sys
from pathlib import Path

DATA_DIR = Path("data")
DOCS_DIR = Path("docs")

MODULES = [
    "src.data_generator",
    "src.production_engine",
    "src.inventory_engine",
    "src.shortage_engine",
    "src.mitigation_engine",
    "src.production_validation",
    "src.capacity_allocator",
    "src.allocation_validation",
    "src.material_allocator",
    "src.anomaly_generator",
    "src.anomaly_detector",
    "src.anomaly_evaluation",
    "src.anomaly_test_cases",
    "src.evaluation_detector",
    "src.evaluation_metrics",
]

FILES = [
    "sku.csv",
    "location.csv",
    "supplier.csv",
    "forecast_demand.csv",
    "inventory.csv",
    "supplier_sku.csv",
    "supplier_capacity.csv",
    "lead_time.csv",
    "purchase_order.csv",
    "bom.csv",
    "production_plan.csv",
    "production_capacity.csv",
    "projected_inventory.csv",
    "shortage.csv",
    "mitigation_option.csv",
    "production_feasibility.csv",
    "component_requirements.csv",
    "capacity_allocation.csv",
    "allocation_validation.csv",
    "material_allocation.csv",
    "ground_truth.csv",
    "anomalies/anomaly_cases.csv",
    "anomalies/detection_results.csv",
    "anomalies/evaluation_input.csv",
    "anomalies/evaluation_ground_truth.csv",
    "anomalies/evaluation_predictions.csv",
]


def checksum(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):
            digest.update(chunk)

    return digest.hexdigest()


def run_modules():
    for module in MODULES:
        print(f"Running {module}...", flush=True)

        subprocess.run(
            [sys.executable, "-m", module],
            check=True
        )


def measure():
    results = {}

    for filename in FILES:
        path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing reproducibility output: {path}"
            )

        with path.open("rb") as file:
            rows = sum(1 for _ in file) - 1

        results[filename] = {
            "rows": rows,
            "sha256": checksum(path)
        }

    return results


def verify_reproducibility():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    print("\n========== FIRST GENERATION ==========")
    run_modules()
    first = measure()

    print("\n========== SECOND GENERATION ==========")
    run_modules()
    second = measure()

    print("\n========== COMPARISON ==========")

    failures = []

    for filename in FILES:
        matching = first[filename] == second[filename]

        print(
            f"{'PASS' if matching else 'FAIL'}: {filename}"
        )

        if not matching:
            failures.append(filename)

    report = {
        "seed": 20261022,
        "datasets_checked": len(FILES),
        "first_run": first,
        "second_run": second,
        "matching": len(failures) == 0,
        "failed_files": failures
    }

    output = DOCS_DIR / "reproducibility_report.json"

    output.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print("\n========== FINAL RESULT ==========")
    print(f"Datasets checked: {len(FILES)}")
    print(f"Mismatches: {len(failures)}")

    if failures:
        raise AssertionError(
            f"Reproducibility failed: {failures}"
        )

    print("SUCCESS: All checked outputs are reproducible!")


if __name__ == "__main__":
    verify_reproducibility()