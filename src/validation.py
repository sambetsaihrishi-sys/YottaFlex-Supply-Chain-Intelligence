import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")


def validate_project():

    print("\n========== YOTTAFLEX VALIDATION ==========\n")

    files = {
        "SKU": "sku.csv",
        "Location": "location.csv",
        "Supplier": "supplier.csv",
        "Forecast Demand": "forecast_demand.csv",
        "Inventory": "inventory.csv",
        "Supplier SKU": "supplier_sku.csv",
        "Supplier Capacity": "supplier_capacity.csv",
        "Lead Time": "lead_time.csv",
        "Purchase Order": "purchase_order.csv",
        "Projected Inventory": "projected_inventory.csv",
        "Shortage": "shortage.csv",
        "Mitigation": "mitigation_option.csv"
    }

    datasets = {}

    for name, filename in files.items():

        path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing required dataset: {filename}"
            )

        df = pd.read_csv(path)
        datasets[name] = df

        print(f"{name}: {len(df):,} records")

    checks = {}

    # Primary key checks
    primary_keys = {
        "SKU": "sku_id",
        "Location": "location_id",
        "Supplier": "supplier_id",
        "Forecast Demand": "demand_id",
        "Inventory": "inventory_id",
        "Supplier SKU": "supplier_sku_id",
        "Supplier Capacity": "capacity_id",
        "Lead Time": "lead_time_id",
        "Purchase Order": "po_id",
        "Shortage": "shortage_id",
        "Mitigation": "mitigation_id"
    }

    for name, column in primary_keys.items():
        checks[f"{name} PK uniqueness"] = (
            datasets[name][column].is_unique
        )

    # Foreign key validation
    checks["Demand SKU references"] = (
        datasets["Forecast Demand"]["sku_id"]
        .isin(datasets["SKU"]["sku_id"])
        .all()
    )

    checks["Demand location references"] = (
        datasets["Forecast Demand"]["location_id"]
        .isin(datasets["Location"]["location_id"])
        .all()
    )

    checks["Purchase order supplier relationships"] = (
        datasets["Purchase Order"]["supplier_sku_id"]
        .isin(datasets["Supplier SKU"]["supplier_sku_id"])
        .all()
    )

    checks["Mitigation shortage references"] = (
        datasets["Mitigation"]["shortage_id"]
        .isin(datasets["Shortage"]["shortage_id"])
        .all()
    )

    # Inventory reconciliation
    projected = datasets["Projected Inventory"]

    checks["Projected inventory reconciliation"] = (
        projected["projected_balance"]
        ==
        (
            projected["opening_balance"]
            + projected["inbound_qty"]
            - projected["forecast_qty"]
        )
    ).all()

    # Mitigation capacity
    mitigation = datasets["Mitigation"]

    checks["Individual mitigation capacity"] = (
        mitigation["proposed_qty"]
        <= mitigation["remaining_capacity"]
    ).all()

    print("\n========== VALIDATION RESULTS ==========\n")

    for check, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {check}")

    failures = [
        check for check, passed in checks.items()
        if not passed
    ]

    print("\n========================================")

    print(f"Total Checks: {len(checks)}")
    print(f"Passed: {len(checks) - len(failures)}")
    print(f"Failed: {len(failures)}")

    if failures:
        raise AssertionError(
            f"Validation failed: {failures}"
        )

    print("\nAll baseline validation checks passed!")


if __name__ == "__main__":
    validate_project()