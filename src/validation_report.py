import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
DOCS_DIR = Path("docs")
DB_PATH = DATA_DIR / "supply_chain.db"


def generate_validation_report():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    checks = {}

    required_files = [
        "sku.csv",
        "location.csv",
        "supplier.csv",
        "forecast_demand.csv",
        "inventory.csv",
        "supplier_sku.csv",
        "supplier_capacity.csv",
        "lead_time.csv",
        "purchase_order.csv",
        "projected_inventory.csv",
        "shortage.csv",
        "mitigation_option.csv",
        "production_plan.csv",
        "production_capacity.csv",
        "bom.csv"
    ]

    checks["Required CSV files exist"] = all(
        (DATA_DIR / filename).exists()
        for filename in required_files
    )

    if not checks["Required CSV files exist"]:
        raise FileNotFoundError(
            "One or more required CSV datasets are missing."
        )

    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    projected = pd.read_csv(DATA_DIR / "projected_inventory.csv")
    shortages = pd.read_csv(DATA_DIR / "shortage.csv")
    mitigations = pd.read_csv(DATA_DIR / "mitigation_option.csv")
    purchase_orders = pd.read_csv(DATA_DIR / "purchase_order.csv")
    production = pd.read_csv(DATA_DIR / "production_plan.csv")
    capacity = pd.read_csv(DATA_DIR / "production_capacity.csv")

    checks["Inventory balance reconciles"] = bool(
        (
            inventory["available_qty"]
            == inventory["on_hand_qty"] - inventory["reserved_qty"]
        ).all()
    )

    checks["Projected balance reconciles"] = bool(
        (
            projected["projected_balance"]
            == (
                projected["opening_balance"]
                + projected["inbound_qty"]
                - projected["forecast_qty"]
            )
        ).all()
    )

    checks["Shortage IDs are unique"] = bool(
        shortages["shortage_id"].is_unique
    )

    checks["Shortage quantities are positive"] = bool(
        (shortages["new_shortage_qty"] > 0).all()
    )

    checks["Mitigation IDs are unique"] = bool(
        mitigations["mitigation_id"].is_unique
    )

    checks["Individual mitigation capacity respected"] = bool(
        (
            mitigations["proposed_qty"]
            <= mitigations["remaining_capacity"]
        ).all()
    )

    checks["Purchase order IDs are unique"] = bool(
        purchase_orders["po_id"].is_unique
    )

    checks["Purchase order quantities are positive"] = bool(
        (purchase_orders["quantity"] > 0).all()
    )

    checks["Production plan IDs are unique"] = bool(
        production["production_plan_id"].is_unique
    )

    checks["Production capacity IDs are unique"] = bool(
        capacity["production_capacity_id"].is_unique
    )

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        fk_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        checks["SQLite foreign keys valid"] = (
            len(fk_errors) == 0
        )

        table_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            """
        ).fetchone()[0]

    finally:
        connection.close()

    passed = sum(checks.values())
    total = len(checks)
    failed = total - passed

    timestamp = datetime.now(timezone.utc).isoformat()

    report = {
        "project": "Supply Chain Intelligence System",
        "seed": 20261022,
        "generated_at_utc": timestamp,
        "database_tables": table_count,
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "checks": checks
    }

    json_path = DOCS_DIR / "validation_summary.json"

    json_path.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    markdown = [
        "# Validation Report",
        "",
        f"Generated at (UTC): {timestamp}",
        "",
        f"Database tables: {table_count}",
        "",
        f"Total checks: {total}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        "",
        "## Validation Results",
        "",
        "| Validation | Result |",
        "|---|---|"
    ]

    for name, result in checks.items():
        status = "PASS" if result else "FAIL"
        markdown.append(f"| {name} | {status} |")

    markdown.extend([
        "",
        "## Scope and Limitations",
        "",
        "These checks cover baseline integrity and arithmetic.",
        "",
        "They do not prove complete production feasibility,",
        "collective mitigation capacity allocation,",
        "or comprehensive lifecycle correctness.",
        "",
        "Additional business-rule testing is required."
    ])

    (DOCS_DIR / "validation_report.md").write_text(
        "\n".join(markdown) + "\n",
        encoding="utf-8"
    )

    print("\n========== VALIDATION REPORT ==========")
    print(f"Total checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    for name, result in checks.items():
        print(f"{'PASS' if result else 'FAIL'}: {name}")

    print("\nReports saved:")
    print("docs/validation_report.md")
    print("docs/validation_summary.json")

    if failed:
        raise AssertionError(
            f"{failed} validation checks failed."
        )


if __name__ == "__main__":
    generate_validation_report()