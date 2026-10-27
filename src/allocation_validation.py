import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")


def validate_allocations():
    allocations = pd.read_csv(
        DATA_DIR / "capacity_allocation.csv"
    )

    capacities = pd.read_csv(
        DATA_DIR / "supplier_capacity.csv"
    )

    purchase_orders = pd.read_csv(
        DATA_DIR / "purchase_order.csv"
    )

    purchase_orders["week"] = (
        pd.to_datetime(purchase_orders["order_date"])
        .dt.strftime("%G-W%V")
        .str.replace("-", "", regex=False)
    )

    committed = (
        purchase_orders.groupby(
            ["supplier_sku_id", "week"],
            as_index=False
        )["quantity"]
        .sum()
        .rename(columns={"quantity": "committed_qty"})
    )

    allocated = (
        allocations.groupby(
            ["supplier_sku_id", "week"],
            as_index=False
        )["allocated_qty"]
        .sum()
    )

    validation = capacities.merge(
        committed,
        on=["supplier_sku_id", "week"],
        how="left",
        validate="one_to_one"
    )

    validation = validation.merge(
        allocated,
        on=["supplier_sku_id", "week"],
        how="left",
        validate="one_to_one"
    )

    validation["committed_qty"] = (
        validation["committed_qty"].fillna(0).astype(int)
    )

    validation["allocated_qty"] = (
        validation["allocated_qty"].fillna(0).astype(int)
    )

    validation["total_usage"] = (
        validation["committed_qty"]
        + validation["allocated_qty"]
    )

    validation["capacity_violation"] = (
        validation["total_usage"]
        > validation["available_capacity"]
    )

    violations = int(
        validation["capacity_violation"].sum()
    )

    print("\n========== ALLOCATION VALIDATION ==========")

    print(f"Capacity records: {len(validation):,}")
    print(f"Capacity violations: {violations:,}")
    print(f"Total allocated units: {allocations['allocated_qty'].sum():,}")

    validation.to_csv(
        DATA_DIR / "allocation_validation.csv",
        index=False
    )

    if violations:
        print("\nWARNING: Some supplier capacities are exceeded.")
    else:
        print("\nPASS: All supplier capacity limits respected.")

    return validation


if __name__ == "__main__":
    validate_allocations()