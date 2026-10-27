from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")


def allocate_supplier_capacity():

    print("\nLoading mitigation and supplier capacity data...")

    mitigations = pd.read_csv(
        DATA_DIR / "mitigation_option.csv"
    )

    purchase_orders = pd.read_csv(
        DATA_DIR / "purchase_order.csv"
    )

    supplier_capacity = pd.read_csv(
        DATA_DIR / "supplier_capacity.csv"
    )

    shortages = pd.read_csv(
        DATA_DIR / "shortage.csv"
    )

    purchase_orders["order_week"] = (
        pd.to_datetime(purchase_orders["order_date"])
        .dt.strftime("%G-W%V")
        .str.replace("-", "", regex=False)
    )

    commitments = (
        purchase_orders.groupby(
            ["supplier_sku_id", "order_week"],
            as_index=False
        )["quantity"]
        .sum()
        .rename(columns={
            "order_week": "week",
            "quantity": "committed_qty"
        })
    )

    capacity = supplier_capacity.merge(
        commitments,
        on=["supplier_sku_id", "week"],
        how="left",
        validate="one_to_one"
    )

    capacity["committed_qty"] = (
        capacity["committed_qty"]
        .fillna(0)
        .astype(int)
    )

    capacity["remaining_capacity"] = (
        capacity["available_capacity"]
        - capacity["committed_qty"]
    ).clip(lower=0)

    capacity_lookup = {
        (row.supplier_sku_id, row.week): int(row.remaining_capacity)
        for row in capacity.itertuples(index=False)
    }

    severity_rank = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3
    }

    shortage_priority = shortages[
        ["shortage_id", "severity", "week"]
    ].copy()

    shortage_priority["priority_rank"] = (
        shortage_priority["severity"]
        .map(severity_rank)
        .fillna(4)
    )

    candidates = mitigations.merge(
        shortage_priority[
            ["shortage_id", "priority_rank"]
        ],
        on="shortage_id",
        validate="many_to_one"
    )

    candidates = candidates[
        candidates["feasible"] == True
    ].copy()

    candidates["order_week"] = (
        pd.to_datetime(candidates["order_date"])
        .dt.strftime("%G-W%V")
        .str.replace("-", "", regex=False)
    )

    candidates = candidates.sort_values(
        [
            "priority_rank",
            "order_date",
            "estimated_unit_cost",
            "mitigation_id"
        ]
    )

    allocated_shortages = set()
    records = []

    for row in candidates.itertuples(index=False):

        if row.shortage_id in allocated_shortages:
            continue

        key = (
            row.supplier_sku_id,
            row.order_week
        )

        available = capacity_lookup.get(key, 0)

        required = int(row.required_qty)

        minimum_order = int(row.minimum_order_qty)

        proposed = min(
            required,
            available
        )

        if proposed < minimum_order:
            continue

        capacity_lookup[key] = available - proposed

        allocated_shortages.add(row.shortage_id)

        records.append({
            "allocation_id": f"ALLOC-{len(records) + 1:08d}",
            "mitigation_id": row.mitigation_id,
            "shortage_id": row.shortage_id,
            "supplier_id": row.supplier_id,
            "supplier_sku_id": row.supplier_sku_id,
            "week": row.order_week,
            "allocated_qty": proposed,
            "estimated_cost": round(
                proposed * float(row.estimated_unit_cost),
                2
            ),
            "status": "PROPOSED"
        })

    columns = [
        "allocation_id",
        "mitigation_id",
        "shortage_id",
        "supplier_id",
        "supplier_sku_id",
        "week",
        "allocated_qty",
        "estimated_cost",
        "status"
    ]

    allocations = pd.DataFrame(
        records,
        columns=columns
    )

    allocations.to_csv(
        DATA_DIR / "capacity_allocation.csv",
        index=False
    )

    print("\n========== CAPACITY ALLOCATION ==========")
    print(f"Feasible Candidates: {len(candidates):,}")
    print(f"Allocations Created: {len(allocations):,}")
    print(f"Total Allocated Units: {allocations['allocated_qty'].sum():,}")
    print("Saved to: data/capacity_allocation.csv")

    return allocations


if __name__ == "__main__":
    allocate_supplier_capacity()