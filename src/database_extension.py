import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "supply_chain.db"

TABLES = {
    "bom": """
        CREATE TABLE IF NOT EXISTS bom (
            bom_id TEXT PRIMARY KEY,
            parent_sku_id TEXT NOT NULL,
            component_sku_id TEXT NOT NULL,
            quantity_per_unit INTEGER NOT NULL
                CHECK(quantity_per_unit > 0),
            effective_from TEXT NOT NULL,
            effective_to TEXT NOT NULL,
            status TEXT NOT NULL,

            FOREIGN KEY(parent_sku_id) REFERENCES sku(sku_id),
            FOREIGN KEY(component_sku_id) REFERENCES sku(sku_id),

            CHECK(effective_from <= effective_to),
            CHECK(parent_sku_id != component_sku_id)
        )
    """,

    "production_capacity": """
        CREATE TABLE IF NOT EXISTS production_capacity (
            production_capacity_id TEXT PRIMARY KEY,
            sku_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            week TEXT NOT NULL,
            maximum_capacity INTEGER NOT NULL
                CHECK(maximum_capacity >= 0),
            status TEXT NOT NULL,

            FOREIGN KEY(sku_id) REFERENCES sku(sku_id),
            FOREIGN KEY(location_id) REFERENCES location(location_id),

            UNIQUE(sku_id, location_id, week)
        )
    """,

    "production_plan": """
        CREATE TABLE IF NOT EXISTS production_plan (
            production_plan_id TEXT PRIMARY KEY,
            sku_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            week TEXT NOT NULL,
            planned_qty INTEGER NOT NULL
                CHECK(planned_qty >= 0),
            status TEXT NOT NULL,

            FOREIGN KEY(sku_id) REFERENCES sku(sku_id),
            FOREIGN KEY(location_id) REFERENCES location(location_id),

            UNIQUE(sku_id, location_id, week)
        )
    """,

    "shortage": """
        CREATE TABLE IF NOT EXISTS shortage (
            shortage_id TEXT PRIMARY KEY,
            sku_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            week TEXT NOT NULL,
            forecast_qty INTEGER NOT NULL,
            inbound_qty INTEGER NOT NULL,
            opening_balance INTEGER NOT NULL,
            projected_balance INTEGER NOT NULL,
            backlog_qty INTEGER NOT NULL,
            new_shortage_qty INTEGER NOT NULL
                CHECK(new_shortage_qty > 0),
            shortage_ratio REAL NOT NULL,
            severity TEXT NOT NULL,
            cause TEXT NOT NULL,
            status TEXT NOT NULL,

            FOREIGN KEY(sku_id) REFERENCES sku(sku_id),
            FOREIGN KEY(location_id) REFERENCES location(location_id),

            UNIQUE(sku_id, location_id, week)
        )
    """,

    "mitigation_option": """
        CREATE TABLE IF NOT EXISTS mitigation_option (
            mitigation_id TEXT PRIMARY KEY,
            shortage_id TEXT NOT NULL,
            sku_id TEXT NOT NULL,
            location_id TEXT NOT NULL,
            supplier_id TEXT NOT NULL,
            supplier_sku_id TEXT NOT NULL,
            required_qty INTEGER NOT NULL,
            proposed_qty INTEGER NOT NULL,
            minimum_order_qty INTEGER NOT NULL,
            remaining_capacity INTEGER NOT NULL,
            lead_time_days INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            arrival_date TEXT NOT NULL,
            estimated_unit_cost REAL NOT NULL,
            estimated_total_cost REAL NOT NULL,
            coverage_ratio REAL NOT NULL,
            on_time INTEGER NOT NULL CHECK(on_time IN (0, 1)),
            feasible INTEGER NOT NULL CHECK(feasible IN (0, 1)),
            recommendation_status TEXT NOT NULL,

            FOREIGN KEY(shortage_id)
                REFERENCES shortage(shortage_id),

            FOREIGN KEY(sku_id) REFERENCES sku(sku_id),
            FOREIGN KEY(location_id) REFERENCES location(location_id),
            FOREIGN KEY(supplier_id) REFERENCES supplier(supplier_id),

            FOREIGN KEY(supplier_sku_id)
                REFERENCES supplier_sku(supplier_sku_id)
        )
    """
}


def extend_database():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run python -m src.database first."
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        for table_name, schema in TABLES.items():
            connection.execute(schema)

            csv_path = DATA_DIR / f"{table_name}.csv"

            if not csv_path.exists():
                raise FileNotFoundError(
                    f"Missing dataset: {csv_path}"
                )

            df = pd.read_csv(csv_path)

            if table_name == "mitigation_option":
                for column in ["on_time", "feasible"]:
                    df[column] = (
                        df[column]
                        .astype(str)
                        .str.lower()
                        .eq("true")
                        .astype(int)
                    )

            existing_count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]

            if existing_count > 0:
                if existing_count != len(df):
                    raise ValueError(
                        f"{table_name} already has {existing_count} "
                        f"rows, but the CSV has {len(df)}. "
                        "Review the database before reloading."
                    )

                print(
                    f"Already loaded: {table_name} "
                    f"({existing_count:,} records)"
                )
                continue

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

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if violations:
            raise ValueError(
                f"Foreign-key violations: {violations[:5]}"
            )

        print("\nAll new tables loaded successfully!")
        print("Foreign-key violations: 0")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    extend_database()