import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")


def calculate_projected_inventory():
    """
    Calculate weekly projected inventory balances using:
    - Initial available inventory
    - Incoming purchase orders
    - Weekly forecast demand
    """

    print("Loading supply chain data...")

    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    demand = pd.read_csv(DATA_DIR / "forecast_demand.csv")
    purchase_orders = pd.read_csv(
        DATA_DIR / "purchase_order.csv"
    )

    # Use revised delivery dates to include transport delays.
    purchase_orders["delivery_date"] = pd.to_datetime(
        purchase_orders["revised_delivery_date"]
    )

    # Convert delivery dates into ISO weeks.
    iso_calendar = purchase_orders[
        "delivery_date"
    ].dt.isocalendar()

    purchase_orders["week"] = (
        iso_calendar["year"].astype(str)
        + "W"
        + iso_calendar["week"].astype(str).str.zfill(2)
    )

    # Only confirmed or delayed orders are included
    # as planned inbound supply.
    eligible_orders = purchase_orders[
        purchase_orders["status"].isin(
            ["CONFIRMED", "DELAYED"]
        )
    ]

    # Aggregate incoming inventory for each SKU-location-week.
    inbound = (
        eligible_orders.groupby(
            ["sku_id", "location_id", "week"],
            as_index=False
        )["quantity"]
        .sum()
        .rename(columns={"quantity": "inbound_qty"})
    )

    # Combine demand with inbound inventory.
    planning = demand.merge(
        inbound,
        on=["sku_id", "location_id", "week"],
        how="left",
        validate="one_to_one"
    )

    planning["inbound_qty"] = (
        planning["inbound_qty"]
        .fillna(0)
        .astype(int)
    )

    # Add initial available inventory.
    opening_inventory = inventory[
        ["sku_id", "location_id", "available_qty"]
    ].rename(
        columns={"available_qty": "initial_inventory"}
    )

    planning = planning.merge(
        opening_inventory,
        on=["sku_id", "location_id"],
        how="left",
        validate="many_to_one"
    )

    if planning["initial_inventory"].isna().any():
        raise ValueError(
            "Some SKU-location combinations have no inventory."
        )

    # Sort chronologically for each SKU-location.
    planning = planning.sort_values(
        ["sku_id", "location_id", "week"]
    ).reset_index(drop=True)

    # Net weekly inventory movement.
    planning["net_change"] = (
        planning["inbound_qty"]
        - planning["forecast_qty"]
    )

    # Calculate cumulative inventory movement.
    planning["cumulative_change"] = (
        planning.groupby(
            ["sku_id", "location_id"]
        )["net_change"].cumsum()
    )

    # Projected balance may be negative to represent
    # unmet demand carried forward.
    planning["projected_balance"] = (
        planning["initial_inventory"]
        + planning["cumulative_change"]
    )

    # Week-by-week opening balance.
    planning["opening_balance"] = (
        planning["projected_balance"]
        - planning["net_change"]
    )

    # Identify negative projected balances.
    planning["shortage_flag"] = (
        planning["projected_balance"] < 0
    )

    # Reconciliation validation.
    expected_balance = (
        planning["opening_balance"]
        + planning["inbound_qty"]
        - planning["forecast_qty"]
    )

    assert (
        planning["projected_balance"]
        == expected_balance
    ).all(), "Inventory reconciliation failed"

    # Save results.
    output_path = DATA_DIR / "projected_inventory.csv"

    planning.to_csv(output_path, index=False)

    print(f"Processed {len(planning):,} planning records")

    print(
        "Weeks with negative projected balances:",
        int(planning["shortage_flag"].sum())
    )

    print(f"Saved to: {output_path}")

    return planning


if __name__ == "__main__":
    calculate_projected_inventory()