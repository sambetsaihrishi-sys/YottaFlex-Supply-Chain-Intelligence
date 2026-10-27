import pandas as pd
import numpy as np
from pathlib import Path

SEED = 20261022
DATA_DIR = Path("data")


def generate_production_data():
    rng = np.random.default_rng(SEED + 500)

    print("\nLoading supply chain datasets...")

    skus = pd.read_csv(DATA_DIR / "sku.csv")
    locations = pd.read_csv(DATA_DIR / "location.csv")
    demand = pd.read_csv(DATA_DIR / "forecast_demand.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")

    finished_goods = skus[
        skus["category"] == "Industrial"
    ].copy()

    components = skus[
        skus["category"] != "Industrial"
    ].copy()

    factories = locations[
        locations["location_type"] == "PRODUCTION_FACILITY"
    ].copy()

    if factories.empty:
        raise ValueError(
            "No production facilities available."
        )

    print(f"Production facilities: {len(factories)}")

    bom_records = []
    production_records = []
    capacity_records = []

    bom_counter = 1
    production_counter = 1
    capacity_counter = 1

    component_ids = set(components["sku_id"])
    selected_products = finished_goods.head(200)

    for product in selected_products.itertuples(index=False):
        sku_id = product.sku_id

        product_demand = demand[
            demand["sku_id"] == sku_id
        ]

        eligible_factories = factories[
            factories["location_id"].isin(
                product_demand["location_id"]
            )
        ]

        if eligible_factories.empty:
            continue

        factory = eligible_factories.iloc[
            int(rng.integers(0, len(eligible_factories)))
        ]

        factory_id = factory["location_id"]

        stocked_components = inventory[
            (inventory["location_id"] == factory_id)
            & (inventory["sku_id"].isin(component_ids))
            & (inventory["available_qty"] > 0)
        ]

        if len(stocked_components) < 2:
            continue

        chosen_components = rng.choice(
            stocked_components["sku_id"].to_numpy(),
            size=2,
            replace=False
        )

        for component_id in chosen_components:
            quantity_per_unit = int(
                rng.integers(1, 5)
            )

            bom_records.append({
                "bom_id": f"BOM-{bom_counter:06d}",
                "parent_sku_id": sku_id,
                "component_sku_id": component_id,
                "quantity_per_unit": quantity_per_unit,
                "effective_from": "2025-12-01",
                "effective_to": "2026-12-31",
                "status": "ACTIVE"
            })

            bom_counter += 1

        factory_demand = product_demand[
            product_demand["location_id"] == factory_id
        ]

        weekly_capacity = int(
            rng.integers(100, 501)
        )

        for week in range(1, 53):
            week_label = f"2026W{week:02d}"

            capacity_records.append({
                "production_capacity_id": (
                    f"PCAP-{capacity_counter:07d}"
                ),
                "sku_id": sku_id,
                "location_id": factory_id,
                "week": week_label,
                "maximum_capacity": weekly_capacity,
                "status": "ACTIVE"
            })

            capacity_counter += 1

            weekly_demand = factory_demand[
                factory_demand["week"] == week_label
            ]

            if weekly_demand.empty:
                continue

            forecast_qty = int(
                weekly_demand["forecast_qty"].iloc[0]
            )

            planned_qty = min(
                forecast_qty,
                weekly_capacity
            )

            production_records.append({
                "production_plan_id": (
                    f"PROD-2026-{production_counter:06d}"
                ),
                "sku_id": sku_id,
                "location_id": factory_id,
                "week": week_label,
                "planned_qty": planned_qty,
                "status": "PLANNED"
            })

            production_counter += 1

    bom = pd.DataFrame(bom_records)
    production = pd.DataFrame(production_records)
    capacity = pd.DataFrame(capacity_records)

    if bom.empty or production.empty or capacity.empty:
        raise ValueError(
            "Production generation returned empty datasets. "
            "Check factory eligibility and inventory coverage."
        )

    assert bom["bom_id"].is_unique, (
        "Duplicate BOM IDs detected."
    )

    assert production["production_plan_id"].is_unique, (
        "Duplicate production plan IDs detected."
    )

    assert capacity["production_capacity_id"].is_unique, (
        "Duplicate production capacity IDs detected."
    )

    assert bom["parent_sku_id"].isin(
        skus["sku_id"]
    ).all(), "Invalid finished product SKU."

    assert bom["component_sku_id"].isin(
        skus["sku_id"]
    ).all(), "Invalid component SKU."

    assert production["sku_id"].isin(
        skus["sku_id"]
    ).all(), "Invalid production SKU."

    assert production["location_id"].isin(
        factories["location_id"]
    ).all(), "Invalid production facility."

    production_check = production.merge(
        capacity[
            [
                "sku_id",
                "location_id",
                "week",
                "maximum_capacity"
            ]
        ],
        on=["sku_id", "location_id", "week"],
        how="left",
        validate="many_to_one"
    )

    assert production_check["maximum_capacity"].notna().all(), (
        "Production plan missing capacity record."
    )

    assert (
        production_check["planned_qty"]
        <= production_check["maximum_capacity"]
    ).all(), "Production capacity exceeded."

    assert (
        production["planned_qty"] >= 0
    ).all(), "Negative production quantity found."

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    bom.to_csv(
        DATA_DIR / "bom.csv",
        index=False
    )

    production.to_csv(
        DATA_DIR / "production_plan.csv",
        index=False
    )

    capacity.to_csv(
        DATA_DIR / "production_capacity.csv",
        index=False
    )

    print("\n========== PRODUCTION GENERATION ==========")

    print(f"BOM records: {len(bom):,}")

    print(f"Production plans: {len(production):,}")

    print(
        f"Production capacity records: {len(capacity):,}"
    )

    print(
        "Unique manufactured products:",
        production["sku_id"].nunique()
    )

    print(
        "Unique production facilities:",
        production["location_id"].nunique()
    )

    print("\nProduction datasets generated successfully!")

    return bom, production, capacity


if __name__ == "__main__":
    generate_production_data()