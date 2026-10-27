import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")


def generate_mitigations():
    """
    Generate supplier-based shortage mitigation recommendations.

    Evaluates:
    - Approved supplier relationships
    - Minimum order quantities
    - Supplier capacity
    - Supplier lead times
    - Delivery feasibility
    - Estimated cost
    """

    print("Loading shortage and supplier data...")

    shortages = pd.read_csv(DATA_DIR / "shortage.csv")
    supplier_sku = pd.read_csv(DATA_DIR / "supplier_sku.csv")
    supplier_capacity = pd.read_csv(DATA_DIR / "supplier_capacity.csv")
    lead_time = pd.read_csv(DATA_DIR / "lead_time.csv")
    purchase_orders = pd.read_csv(DATA_DIR / "purchase_order.csv")
    skus = pd.read_csv(DATA_DIR / "sku.csv")

    # Only approved suppliers can be used.
    approved = supplier_sku[
        supplier_sku["approval_status"] == "APPROVED"
    ].copy()

    # Add supplier lead times.
    approved = approved.merge(
        lead_time[
            ["supplier_sku_id", "lead_time_days"]
        ],
        on="supplier_sku_id",
        validate="one_to_one"
    )

    # Add unit costs.
    approved = approved.merge(
        skus[["sku_id", "unit_cost"]],
        on="sku_id",
        validate="many_to_one"
    )

    # Calculate capacity already committed to purchase orders.
    purchase_orders["order_week"] = (
        pd.to_datetime(purchase_orders["order_date"])
        .dt.isocalendar()
        .apply(
            lambda row: f"{row['year']}W{int(row['week']):02d}",
            axis=1
        )
    )

    committed_capacity = (
        purchase_orders.groupby(
            ["supplier_sku_id", "order_week"],
            as_index=False
        )["quantity"]
        .sum()
        .rename(
            columns={
                "order_week": "week",
                "quantity": "committed_qty"
            }
        )
    )

    capacity = supplier_capacity.merge(
        committed_capacity,
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

    # Candidate supplier options for each shortage.
    candidates = shortages.merge(
        approved,
        on="sku_id",
        how="left",
        validate="many_to_many"
    )

    # Shortage week start (ISO calendar).
    candidates["shortage_date"] = pd.to_datetime(
        candidates["week"].astype(str) + "1",
        format="%GW%V%u"
    )

    # Planning assumption: mitigation orders are evaluated
    # as if placed at the start of their shortage week.
    candidates["order_date"] = candidates["shortage_date"]

    candidates["arrival_date"] = (
        candidates["order_date"]
        + pd.to_timedelta(
            candidates["lead_time_days"],
            unit="D"
        )
    )

    # Check supplier capacity for proposed order week.
    candidates = candidates.merge(
        capacity[
            [
                "supplier_sku_id",
                "week",
                "remaining_capacity"
            ]
        ],
        on=["supplier_sku_id", "week"],
        how="left",
        validate="many_to_one"
    )

    candidates["remaining_capacity"] = (
        candidates["remaining_capacity"]
        .fillna(0)
        .astype(int)
    )

    # Quantity supplier can potentially provide.
    candidates["required_qty"] = (
        candidates["new_shortage_qty"]
    )

    candidates["proposed_qty"] = candidates[
        ["required_qty", "remaining_capacity"]
    ].min(axis=1)

    # Respect minimum order quantities.
    candidates["meets_moq"] = (
        candidates["proposed_qty"]
        >= candidates["minimum_order_qty"]
    )

    # Can the supplier deliver during the shortage week?
    candidates["on_time"] = (
        candidates["arrival_date"]
        <= (
            candidates["shortage_date"]
            + pd.Timedelta(days=6)
        )
    )

    candidates["feasible"] = (
        candidates["meets_moq"]
        & candidates["on_time"]
        & (candidates["proposed_qty"] > 0)
    )

    # Synthetic expedited purchasing premium.
    candidates["estimated_unit_cost"] = (
        candidates["unit_cost"] * 1.10
    ).round(2)

    candidates["estimated_total_cost"] = (
        candidates["proposed_qty"]
        * candidates["estimated_unit_cost"]
    ).round(2)

    candidates["coverage_ratio"] = (
        candidates["proposed_qty"]
        / candidates["required_qty"].clip(lower=1)
    ).round(4)

    # Rank feasible options first, then coverage and cost.
    candidates = candidates.sort_values(
        [
            "shortage_id",
            "feasible",
            "coverage_ratio",
            "estimated_total_cost"
        ],
        ascending=[True, False, False, True]
    ).reset_index(drop=True)

    candidates["option_number"] = (
        candidates.groupby("shortage_id").cumcount() + 1
    )

    candidates["mitigation_id"] = (
        "MIT-"
        + candidates["shortage_id"]
        + "-"
        + candidates["option_number"].astype(str).str.zfill(2)
    )

    candidates["recommendation_status"] = "NOT_FEASIBLE"

    candidates.loc[
        candidates["feasible"],
        "recommendation_status"
    ] = "FEASIBLE"

    output_columns = [
        "mitigation_id",
        "shortage_id",
        "sku_id",
        "location_id",
        "supplier_id",
        "supplier_sku_id",
        "required_qty",
        "proposed_qty",
        "minimum_order_qty",
        "remaining_capacity",
        "lead_time_days",
        "order_date",
        "arrival_date",
        "estimated_unit_cost",
        "estimated_total_cost",
        "coverage_ratio",
        "on_time",
        "feasible",
        "recommendation_status"
    ]

    mitigations = candidates[output_columns]

    assert mitigations["mitigation_id"].is_unique

    assert (
        mitigations["proposed_qty"]
        <= mitigations["remaining_capacity"]
    ).all()

    output_path = DATA_DIR / "mitigation_option.csv"

    mitigations.to_csv(output_path, index=False)

    print(
        f"Generated {len(mitigations):,} mitigation options"
    )

    print(
        "Feasible options:",
        int(mitigations["feasible"].sum())
    )

    print(
        "Not feasible:",
        int((~mitigations["feasible"]).sum())
    )

    print(f"Saved to: {output_path}")

    return mitigations


if __name__ == "__main__":
    generate_mitigations()