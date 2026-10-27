from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")


def test_sku_count():
    df = pd.read_csv(DATA_DIR / "sku.csv")

    assert len(df) == 3000


def test_location_count():
    df = pd.read_csv(DATA_DIR / "location.csv")

    assert len(df) == 50


def test_supplier_count():
    df = pd.read_csv(DATA_DIR / "supplier.csv")

    assert len(df) == 500


def test_demand_count():
    df = pd.read_csv(DATA_DIR / "forecast_demand.csv")

    assert len(df) == 468000


def test_purchase_order_count():
    df = pd.read_csv(DATA_DIR / "purchase_order.csv")

    assert len(df) == 10000


def test_primary_keys_unique():
    datasets = {
        "sku.csv": "sku_id",
        "location.csv": "location_id",
        "supplier.csv": "supplier_id",
        "forecast_demand.csv": "demand_id",
        "purchase_order.csv": "po_id"
    }

    for filename, key in datasets.items():
        df = pd.read_csv(DATA_DIR / filename)

        assert df[key].is_unique, (
            f"Duplicate primary key found in {filename}"
        )