from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")


def test_shortage_ids_unique():
    df = pd.read_csv(DATA_DIR / "shortage.csv")

    assert df["shortage_id"].is_unique


def test_shortage_quantities_positive():
    df = pd.read_csv(DATA_DIR / "shortage.csv")

    assert (df["new_shortage_qty"] > 0).all()


def test_shortage_severity_values():
    df = pd.read_csv(DATA_DIR / "shortage.csv")

    valid_values = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    }

    assert df["severity"].isin(valid_values).all()


def test_shortage_backlog_consistency():
    df = pd.read_csv(DATA_DIR / "shortage.csv")

    expected_backlog = (
        -df["projected_balance"]
    ).clip(lower=0)

    assert (df["backlog_qty"] == expected_backlog).all()


def test_shortage_foreign_keys():
    shortages = pd.read_csv(DATA_DIR / "shortage.csv")
    skus = pd.read_csv(DATA_DIR / "sku.csv")
    locations = pd.read_csv(DATA_DIR / "location.csv")

    assert shortages["sku_id"].isin(skus["sku_id"]).all()
    assert shortages["location_id"].isin(
        locations["location_id"]
    ).all()