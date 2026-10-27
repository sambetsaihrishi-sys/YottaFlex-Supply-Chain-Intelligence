import sqlite3
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "supply_chain.db"


ALLOWED_TRANSITIONS = {
    None: {"CREATED"},
    "CREATED": {"CONFIRMED", "CANCELLED"},
    "CONFIRMED": {"IN_TRANSIT", "DELAYED", "CANCELLED"},
    "IN_TRANSIT": {"DELAYED", "DELIVERED"},
    "DELAYED": {"IN_TRANSIT", "DELIVERED", "CANCELLED"},
    "DELIVERED": set(),
    "CANCELLED": set()
}


def create_event_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS purchase_order_event (
            event_id TEXT PRIMARY KEY,
            po_id TEXT NOT NULL,
            previous_status TEXT,
            new_status TEXT NOT NULL,
            event_timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,

            FOREIGN KEY (po_id)
                REFERENCES purchase_order(po_id)
        )
    """)


def add_event(
    connection,
    po_id,
    new_status,
    timestamp
):
    exists = connection.execute(
        "SELECT 1 FROM purchase_order WHERE po_id = ?",
        (po_id,)
    ).fetchone()

    if not exists:
        raise ValueError(f"Unknown purchase order: {po_id}")

    previous = connection.execute(
        """
        SELECT new_status, event_timestamp
        FROM purchase_order_event
        WHERE po_id = ?
        ORDER BY event_timestamp DESC, event_id DESC
        LIMIT 1
        """,
        (po_id,)
    ).fetchone()

    previous_status = previous[0] if previous else None

    allowed = ALLOWED_TRANSITIONS.get(previous_status, set())

    if new_status not in allowed:
        raise ValueError(
            f"Invalid transition: {previous_status} -> {new_status}"
        )

    if previous and timestamp <= previous[1]:
        raise ValueError(
            "Event timestamps must increase chronologically."
        )

    counter = connection.execute(
        "SELECT COUNT(*) FROM purchase_order_event"
    ).fetchone()[0] + 1

    event_id = f"EVT-{counter:08d}"

    connection.execute(
        """
        INSERT INTO purchase_order_event (
            event_id,
            po_id,
            previous_status,
            new_status,
            event_timestamp,
            event_type
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            po_id,
            previous_status,
            new_status,
            timestamp,
            f"STATUS_CHANGED_TO_{new_status}"
        )
    )

    return event_id


def generate_event_history():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run database setup first."
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        create_event_table(connection)

        existing = connection.execute(
            "SELECT COUNT(*) FROM purchase_order_event"
        ).fetchone()[0]

        if existing > 0:
            print(
                f"Event history already exists: {existing:,} events"
            )
            return

        purchase_orders = pd.read_csv(
            DATA_DIR / "purchase_order.csv"
        )

        for po in purchase_orders.itertuples(index=False):
            order_date = pd.Timestamp(po.order_date)

            created_at = order_date.replace(
                hour=8, minute=0, second=0
            )

            confirmed_at = order_date.replace(
                hour=9, minute=0, second=0
            )

            add_event(
                connection,
                po.po_id,
                "CREATED",
                created_at.isoformat()
            )

            add_event(
                connection,
                po.po_id,
                "CONFIRMED",
                confirmed_at.isoformat()
            )

            if bool(po.transport_delayed):
                delayed_at = order_date.replace(
                    hour=10, minute=0, second=0
                )

                add_event(
                    connection,
                    po.po_id,
                    "DELAYED",
                    delayed_at.isoformat()
                )

        connection.commit()

        events = pd.read_sql_query(
            "SELECT * FROM purchase_order_event",
            connection
        )

        events.to_csv(
            DATA_DIR / "purchase_order_events.csv",
            index=False
        )

        print("\n========== EVENT HISTORY ==========")
        print(f"Purchase Orders: {len(purchase_orders):,}")
        print(f"Events Generated: {len(events):,}")
        print(f"Duplicate Event IDs: {events['event_id'].duplicated().sum()}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    generate_event_history()