import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("data")


def generate_shortages():
    """
    Identify incremental shortages from projected inventory.

    Negative projected balances represent outstanding backlog.
    New shortages are additional unmet quantities, not the
    entire negative balance repeated every week.
    """

    print("Loading projected inventory...")

    planning = pd.read_csv(
        DATA_DIR / "projected_inventory.csv"
    )

    planning = planning.sort_values(
        ["sku_id", "location_id", "week"]
    ).reset_index(drop=True)

    # Convert negative projected balances into backlog amounts.
    planning["backlog_qty"] = (
        -planning["projected_balance"]
    ).clip(lower=0)

    # Previous week's outstanding backlog.
    planning["previous_backlog"] = (
        planning.groupby(["sku_id", "location_id"])[
            "backlog_qty"
        ]
        .shift(1)
        .fillna(0)
    )

    # Additional unmet demand introduced during the week.
    planning["new_shortage_qty"] = (
        planning["backlog_qty"]
        - planning["previous_backlog"]
    ).clip(lower=0)

    # Select weeks where new shortages occur.
    shortages = planning[
        planning["new_shortage_qty"] > 0
    ].copy()

    # Prioritize using the additional shortage relative
    # to that week's forecast demand.
    shortages["shortage_ratio"] = (
        shortages["new_shortage_qty"]
        / shortages["forecast_qty"].clip(lower=1)
    )

    conditions = [
        shortages["shortage_ratio"] >= 0.75,
        shortages["shortage_ratio"] >= 0.40,
        shortages["shortage_ratio"] >= 0.15
    ]

    choices = [
        "CRITICAL",
        "HIGH",
        "MEDIUM"
    ]

    shortages["severity"] = np.select(
        conditions,
        choices,
        default="LOW"
    )

    # Preliminary cause classifications.
    # These are heuristic explanations, not verified
    # root-cause labels.
    shortages["cause"] = "INSUFFICIENT_SUPPLY"

    shortages.loc[
        shortages["demand_spike"].astype(str).str.lower()
        == "true",
        "cause"
    ] = "DEMAND_SPIKE"

    shortages.loc[
        (shortages["inbound_qty"] == 0)
        & (
            shortages["cause"]
            == "INSUFFICIENT_SUPPLY"
        ),
        "cause"
    ] = "NO_SCHEDULED_INBOUND"

    # Deterministic shortage IDs.
    shortages = shortages.reset_index(drop=True)

    shortages["shortage_id"] = [
        f"SHORT-2026-{i:06d}"
        for i in range(1, len(shortages) + 1)
    ]

    shortages["status"] = "OPEN"

    # Select important output fields.
    output_columns = [
        "shortage_id",
        "sku_id",
        "location_id",
        "week",
        "forecast_qty",
        "inbound_qty",
        "opening_balance",
        "projected_balance",
        "backlog_qty",
        "new_shortage_qty",
        "shortage_ratio",
        "severity",
        "cause",
        "status"
    ]

    shortages = shortages[output_columns]

    # Basic validations.
    assert shortages["shortage_id"].is_unique

    assert (
        shortages["new_shortage_qty"] > 0
    ).all()

    assert shortages[
        ["sku_id", "location_id", "week"]
    ].duplicated().sum() == 0

    output_path = DATA_DIR / "shortage.csv"

    shortages.to_csv(output_path, index=False)

    print(
        f"Generated {len(shortages):,} shortage records"
    )

    print("\nSeverity Distribution:")

    print(
        shortages["severity"].value_counts()
    )

    print(f"\nSaved to: {output_path}")

    return shortages


if __name__ == "__main__":
    generate_shortages()