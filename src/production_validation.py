from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")


def validate_production():
    """
    Assess production feasibility using:
    1. Weekly production capacity
    2. BOM component requirements
    3. Starting component inventory at the production location

    This is a preliminary material check.
    It does not schedule component consumption across weeks.
    """

    print("\nLoading production datasets...")

    production = pd.read_csv(
        DATA_DIR / "production_plan.csv"
    )

    capacity = pd.read_csv(
        DATA_DIR / "production_capacity.csv"
    )

    bom = pd.read_csv(
        DATA_DIR / "bom.csv"
    )

    inventory = pd.read_csv(
        DATA_DIR / "inventory.csv"
    )

    # Validate essential inputs before joining.
    if production.empty:
        raise ValueError(
            "No production plans were generated. "
            "Review the factory-location assignment."
        )

    if bom.empty:
        raise ValueError("BOM dataset is empty.")

    if capacity.empty:
        raise ValueError("Production capacity dataset is empty.")

    # Each finished SKU should have one capacity record
    # per factory and week.
    capacity_keys = ["sku_id", "location_id", "week"]

    if capacity.duplicated(capacity_keys).any():
        raise ValueError("Duplicate production capacity records.")

    # Attach weekly capacity to each production plan.
    plans = production.merge(
        capacity[
            capacity_keys + ["maximum_capacity"]
        ],
        on=capacity_keys,
        how="left",
        validate="many_to_one",
        indicator=True
    )

    if (plans["_merge"] != "both").any():
        raise ValueError(
            "Some production plans have no capacity record."
        )

    plans = plans.drop(columns="_merge")

    plans["capacity_valid"] = (
        (plans["planned_qty"] >= 0)
        & (
            plans["planned_qty"]
            <= plans["maximum_capacity"]
        )
    )

    # Attach BOM components to production plans.
    component_requirements = plans.merge(
        bom[
            [
                "parent_sku_id",
                "component_sku_id",
                "quantity_per_unit"
            ]
        ],
        left_on="sku_id",
        right_on="parent_sku_id",
        how="left",
        validate="many_to_many"
    )

    if component_requirements["component_sku_id"].isna().any():
        raise ValueError(
            "Some production plans have no BOM components."
        )

    # Derived component requirement:
    # Production quantity × quantity per finished product.
    component_requirements["required_component_qty"] = (
        component_requirements["planned_qty"]
        * component_requirements["quantity_per_unit"]
    )

    # Inventory available for each component at each factory.
    component_stock = inventory[
        [
            "sku_id",
            "location_id",
            "available_qty"
        ]
    ].rename(
        columns={
            "sku_id": "component_sku_id",
            "available_qty": "component_available_qty"
        }
    )

    component_requirements = component_requirements.merge(
        component_stock,
        on=["component_sku_id", "location_id"],
        how="left",
        validate="many_to_one"
    )

    # Missing inventory is explicitly treated as zero
    # available component stock.
    component_requirements["component_available_qty"] = (
        component_requirements["component_available_qty"]
        .fillna(0)
        .astype(int)
    )

    component_requirements["component_sufficient"] = (
        component_requirements["component_available_qty"]
        >= component_requirements["required_component_qty"]
    )

    # Every component must be available for the plan
    # to pass this preliminary material check.
    material_summary = (
        component_requirements.groupby(
            "production_plan_id",
            as_index=False
        )["component_sufficient"]
        .all()
        .rename(
            columns={
                "component_sufficient": "materials_valid"
            }
        )
    )

    plans = plans.merge(
        material_summary,
        on="production_plan_id",
        validate="one_to_one"
    )

    plans["preliminary_feasible"] = (
        plans["capacity_valid"]
        & plans["materials_valid"]
    )

    plans["validation_status"] = "NEEDS_REVIEW"

    plans.loc[
        plans["preliminary_feasible"],
        "validation_status"
    ] = "PRELIMINARY_PASS"

    # Preserve original plans; export separate results.
    plans.to_csv(
        DATA_DIR / "production_feasibility.csv",
        index=False
    )

    component_requirements.to_csv(
        DATA_DIR / "component_requirements.csv",
        index=False
    )

    print("\n========== PRODUCTION VALIDATION ==========")

    print(f"Production Plans: {len(plans):,}")

    print(
        "Capacity Valid:",
        int(plans["capacity_valid"].sum())
    )

    print(
        "Preliminary Feasible:",
        int(plans["preliminary_feasible"].sum())
    )

    print(
        "Needs Review:",
        int((~plans["preliminary_feasible"]).sum())
    )

    print(
        "Component Requirement Records:",
        len(component_requirements)
    )

    print("\nFiles generated:")
    print("data/production_feasibility.csv")
    print("data/component_requirements.csv")

    return plans, component_requirements


if __name__ == "__main__":
    validate_production()