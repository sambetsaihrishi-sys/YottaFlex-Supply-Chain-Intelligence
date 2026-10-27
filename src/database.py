import sqlite3
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "supply_chain.db"


def create_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        connection.executescript("""
            CREATE TABLE IF NOT EXISTS sku (
                sku_id TEXT PRIMARY KEY,
                sku_name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_of_measure TEXT NOT NULL,
                unit_cost REAL NOT NULL CHECK(unit_cost >= 0),
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS location (
                location_id TEXT PRIMARY KEY,
                location_name TEXT NOT NULL,
                city TEXT NOT NULL,
                location_type TEXT NOT NULL,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS supplier (
                supplier_id TEXT PRIMARY KEY,
                supplier_name TEXT NOT NULL,
                country TEXT NOT NULL,
                supplier_type TEXT NOT NULL,
                reliability_score REAL NOT NULL
                    CHECK(reliability_score BETWEEN 0 AND 1),
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS forecast_demand (
                demand_id TEXT PRIMARY KEY,
                sku_id TEXT NOT NULL,
                location_id TEXT NOT NULL,
                week TEXT NOT NULL,
                forecast_qty INTEGER NOT NULL
                    CHECK(forecast_qty >= 0),
                demand_spike INTEGER NOT NULL
                    CHECK(demand_spike IN (0, 1)),
                status TEXT NOT NULL,

                FOREIGN KEY(sku_id) REFERENCES sku(sku_id),
                FOREIGN KEY(location_id)
                    REFERENCES location(location_id),

                UNIQUE(sku_id, location_id, week)
            );

            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id TEXT PRIMARY KEY,
                sku_id TEXT NOT NULL,
                location_id TEXT NOT NULL,
                snapshot_date TEXT NOT NULL,
                on_hand_qty INTEGER NOT NULL
                    CHECK(on_hand_qty >= 0),
                reserved_qty INTEGER NOT NULL
                    CHECK(reserved_qty >= 0),
                available_qty INTEGER NOT NULL
                    CHECK(available_qty >= 0),
                unit_of_measure TEXT NOT NULL,
                status TEXT NOT NULL,

                FOREIGN KEY(sku_id) REFERENCES sku(sku_id),
                FOREIGN KEY(location_id)
                    REFERENCES location(location_id),

                CHECK(
                    available_qty = on_hand_qty - reserved_qty
                ),

                UNIQUE(sku_id, location_id, snapshot_date)
            );

            CREATE TABLE IF NOT EXISTS supplier_sku (
                supplier_sku_id TEXT PRIMARY KEY,
                supplier_id TEXT NOT NULL,
                sku_id TEXT NOT NULL,
                minimum_order_qty INTEGER NOT NULL
                    CHECK(minimum_order_qty > 0),
                approval_status TEXT NOT NULL
                    CHECK(
                        approval_status IN (
                            'APPROVED',
                            'PENDING',
                            'REJECTED'
                        )
                    ),
                effective_from TEXT NOT NULL,
                effective_to TEXT NOT NULL,

                FOREIGN KEY(supplier_id)
                    REFERENCES supplier(supplier_id),

                FOREIGN KEY(sku_id)
                    REFERENCES sku(sku_id),

                UNIQUE(supplier_id, sku_id),

                CHECK(effective_from <= effective_to)
            );

            CREATE TABLE IF NOT EXISTS supplier_capacity (
                capacity_id TEXT PRIMARY KEY,
                supplier_sku_id TEXT NOT NULL,
                supplier_id TEXT NOT NULL,
                sku_id TEXT NOT NULL,
                week TEXT NOT NULL,
                maximum_capacity INTEGER NOT NULL
                    CHECK(maximum_capacity >= 0),
                available_capacity INTEGER NOT NULL
                    CHECK(available_capacity >= 0),
                capacity_constrained INTEGER NOT NULL
                    CHECK(capacity_constrained IN (0, 1)),

                FOREIGN KEY(supplier_sku_id)
                    REFERENCES supplier_sku(supplier_sku_id),

                CHECK(
                    available_capacity <= maximum_capacity
                ),

                UNIQUE(supplier_sku_id, week)
            );

            CREATE TABLE IF NOT EXISTS lead_time (
                lead_time_id TEXT PRIMARY KEY,
                supplier_sku_id TEXT NOT NULL,
                supplier_id TEXT NOT NULL,
                sku_id TEXT NOT NULL,
                lead_time_days INTEGER NOT NULL
                    CHECK(lead_time_days > 0),
                effective_from TEXT NOT NULL,
                effective_to TEXT NOT NULL,

                FOREIGN KEY(supplier_sku_id)
                    REFERENCES supplier_sku(supplier_sku_id),

                CHECK(effective_from <= effective_to)
            );

            CREATE TABLE IF NOT EXISTS purchase_order (
                po_id TEXT PRIMARY KEY,
                supplier_sku_id TEXT NOT NULL,
                supplier_id TEXT NOT NULL,
                sku_id TEXT NOT NULL,
                location_id TEXT NOT NULL,
                order_date TEXT NOT NULL,
                expected_delivery_date TEXT NOT NULL,
                revised_delivery_date TEXT NOT NULL,
                quantity INTEGER NOT NULL
                    CHECK(quantity > 0),
                unit_of_measure TEXT NOT NULL,
                status TEXT NOT NULL
                    CHECK(
                        status IN (
                            'CONFIRMED',
                            'DELAYED'
                        )
                    ),
                transport_delayed INTEGER NOT NULL
                    CHECK(transport_delayed IN (0, 1)),
                delay_days INTEGER NOT NULL
                    CHECK(delay_days >= 0),

                FOREIGN KEY(supplier_sku_id)
                    REFERENCES supplier_sku(supplier_sku_id),

                FOREIGN KEY(location_id)
                    REFERENCES location(location_id),

                CHECK(
                    order_date <= expected_delivery_date
                ),

                CHECK(
                    expected_delivery_date <= revised_delivery_date
                )
            );
        """)

        connection.commit()
        print("SQLite database schema created successfully!")

    finally:
        connection.close()


def load_master_data():
    datasets = [
        ("sku", "sku.csv"),
        ("location", "location.csv"),
        ("supplier", "supplier.csv"),
        ("forecast_demand", "forecast_demand.csv"),
        ("inventory", "inventory.csv"),
        ("supplier_sku", "supplier_sku.csv"),
        ("supplier_capacity", "supplier_capacity.csv"),
        ("lead_time", "lead_time.csv"),
        ("purchase_order", "purchase_order.csv")
    ]

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        for table_name, filename in datasets:
            file_path = DATA_DIR / filename

            if not file_path.exists():
                raise FileNotFoundError(
                    f"Missing dataset: {filename}"
                )

            df = pd.read_csv(file_path)

            if table_name == "forecast_demand":
                df["demand_spike"] = (
                    df["demand_spike"]
                    .astype(str)
                    .str.lower()
                    .eq("true")
                    .astype(int)
                )

            if table_name == "supplier_capacity":
                df["capacity_constrained"] = (
                    df["capacity_constrained"]
                    .astype(str)
                    .str.lower()
                    .eq("true")
                    .astype(int)
                )

            if table_name == "purchase_order":
                df["transport_delayed"] = (
                    df["transport_delayed"]
                    .astype(str)
                    .str.lower()
                    .eq("true")
                    .astype(int)
                )

            df.to_sql(
                table_name,
                connection,
                if_exists="append",
                index=False,
                chunksize=1000
            )

            print(
                f"Loaded {len(df):,} records into {table_name}"
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def verify_database():
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        tables = [
            "sku",
            "location",
            "supplier",
            "forecast_demand",
            "inventory",
            "supplier_sku",
            "supplier_capacity",
            "lead_time",
            "purchase_order"
        ]

        print("\n========== DATABASE VERIFICATION ==========")

        for table in tables:
            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]

            print(f"{table}: {count:,} records")

        foreign_key_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print(
            f"\nForeign key violations: {len(foreign_key_errors)}"
        )

        if foreign_key_errors:
            raise ValueError(
                f"Foreign key violations found: "
                f"{foreign_key_errors[:5]}"
            )

        print("\nDatabase verification completed successfully!")

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()
    load_master_data()
    verify_database()