from pathlib import Path
from collections import defaultdict

import pandas as pd


DATA_DIR = Path("data")


def allocate_production_materials():

    print("\nLoading production and inventory data...")

    production = pd.read_csv(
        DATA_DIR / "production_plan.csv"
    )

    bom = pd.read_csv(
        DATA_DIR / "bom.csv"
    )

    inventory = pd.read_csv(
        DATA_DIR / "inventory.csv"
    )

    capacity = pd.read_csv(
        DATA_DIR / "production_capacity.csv"
    )

    purchase_orders = pd.read_csv(
        DATA_DIR / "purchase_order.csv"
    )

    material_stock = defaultdict(int)

    for row in inventory.itertuples(index=False):
        material_stock[
            (row.sku_id, row.location_id)
        ] += int(row.available_qty)

    bom_lookup = defaultdict(list)

    for row in bom.itertuples(index=False):
        bom_lookup[row.parent_sku_id].append(
            (row.component_sku_id, int(row.quantity_per_unit))
        )

    capacity_lookup = {
        (row.sku_id, row.location_id, row.week):
        int(row.maximum_capacity)
        for row in capacity.itertuples(index=False)
    }

    purchase_orders["arrival_date"] = pd.to_datetime(
        purchase_orders["revised_delivery_date"]
    )

    iso = purchase_orders["arrival_date"].dt.isocalendar()

    purchase_orders["arrival_week"] = (
        iso["year"].astype(str)
        + "W"
        + iso["week"].astype(str).str.zfill(2)
    )

    inbound_lookup = defaultdict(list)

    eligible_orders = purchase_orders[
        purchase_orders["status"].isin(
            ["CONFIRMED", "DELAYED"]
        )
    ]

    for row in eligible_orders.itertuples(index=False):
        inbound_lookup[row.arrival_week].append(
            (
                row.sku_id,
                row.location_id,
                int(row.quantity)
            )
        )

    production = production.sort_values(
        ["week", "production_plan_id"]
    )

    records = []
    applied_inbound_weeks = set()

    for plan in production.itertuples(index=False):

        if plan.week not in applied_inbound_weeks:
            for sku_id, location_id, quantity in inbound_lookup.get(
                plan.week, []
            ):
                material_stock[(sku_id, location_id)] += quantity

            applied_inbound_weeks.add(plan.week)

        required = int(plan.planned_qty)

        max_capacity = capacity_lookup.get(
            (plan.sku_id, plan.location_id, plan.week),
            0
        )

        components = bom_lookup.get(plan.sku_id, [])

        feasible_qty = min(required, max_capacity)

        if not components:
            feasible_qty = 0

        for component_id, qty_per_unit in components:
            available = material_stock[
                (component_id, plan.location_id)
            ]

            feasible_qty = min(
                feasible_qty,
                available // qty_per_unit
            )

        feasible_qty = max(0, int(feasible_qty))

        for component_id, qty_per_unit in components:
            material_stock[
                (component_id, plan.location_id)
            ] -= feasible_qty * qty_per_unit

        records.append({
            "production_plan_id": plan.production_plan_id,
            "sku_id": plan.sku_id,
            "location_id": plan.location_id,
            "week": plan.week,
            "planned_qty": required,
            "feasible_qty": feasible_qty,
            "unfulfilled_qty": required - feasible_qty,
            "capacity_limit": max_capacity,
            "status": (
                "FEASIBLE" if feasible_qty == required
                else "PARTIAL" if feasible_qty > 0
                else "BLOCKED"
            )
        })

    result = pd.DataFrame(records)

    result.to_csv(
        DATA_DIR / "material_allocation.csv",
        index=False
    )

    print("\n========== MATERIAL ALLOCATION ==========")
    print(f"Production plans: {len(result):,}")
    print(f"Fully feasible: {(result['status'] == 'FEASIBLE').sum():,}")
    print(f"Partially feasible: {(result['status'] == 'PARTIAL').sum():,}")
    print(f"Blocked: {(result['status'] == 'BLOCKED').sum():,}")
    print(f"Total feasible production units: {result['feasible_qty'].sum():,}")

    print("\nSaved to: data/material_allocation.csv")

    return result


if __name__ == "__main__":
    allocate_production_materials()