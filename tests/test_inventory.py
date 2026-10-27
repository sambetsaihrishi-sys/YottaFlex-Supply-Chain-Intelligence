from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")


def test_inventory_reconciliation():
    df = pd.read_csv(DATA_DIR / "projected_inventory.csv")

    expected = (
        df["opening_balance"]
        + df["inbound_qty"]
        - df["forecast_qty"]
    )

    assert (df["projected_balance"] == expected).all()


def test_inventory_non_negative_source():
    df = pd.read_csv(DATA_DIR / "inventory.csv")

    assert (df["on_hand_qty"] >= 0).all()
    assert (df["reserved_qty"] >= 0).all()
    assert (df["available_qty"] >= 0).all()


def test_inventory_available_quantity():
    df = pd.read_csv(DATA_DIR / "inventory.csv")

    assert (
        df["available_qty"]
        == df["on_hand_qty"] - df["reserved_qty"]
    ).all()


def test_no_duplicate_inventory_ids():
    df = pd.read_csv(DATA_DIR / "inventory.csv")

    assert df["inventory_id"].is_unique