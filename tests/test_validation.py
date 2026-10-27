import sqlite3

import pandas as pd


DB_PATH = "data/supply_chain.db"


def test_database_foreign_keys():
    connection = sqlite3.connect(DB_PATH)

    try:
        errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        assert len(errors) == 0

    finally:
        connection.close()


def test_purchase_order_quantity():
    df = pd.read_csv("data/purchase_order.csv")

    assert (df["quantity"] > 0).all()


def test_purchase_order_dates():
    df = pd.read_csv("data/purchase_order.csv")

    order_date = pd.to_datetime(df["order_date"])

    expected = pd.to_datetime(
        df["expected_delivery_date"]
    )

    revised = pd.to_datetime(
        df["revised_delivery_date"]
    )

    assert (expected >= order_date).all()
    assert (revised >= expected).all()


def test_supplier_capacity_limits():
    df = pd.read_csv("data/supplier_capacity.csv")

    assert (
        df["available_capacity"]
        <= df["maximum_capacity"]
    ).all()

    assert (df["available_capacity"] >= 0).all()


def test_production_capacity():
    df = pd.read_csv("data/production_feasibility.csv")

    assert df["capacity_valid"].all()