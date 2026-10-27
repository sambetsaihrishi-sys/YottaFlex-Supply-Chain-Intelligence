import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/supply_chain.db")
DOCS_DIR = Path("docs")


def generate_data_dictionary():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    try:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name",
            connection
        )["name"].tolist()

        lines = [
            "# Supply Chain Data Dictionary",
            "",
            "## Overview",
            "",
            "This document describes the database tables "
            "and their fields.",
            "",
            "Data is synthetically generated using seed 20261022.",
            ""
        ]

        for table in tables:
            lines.append(f"## {table}")
            lines.append("")

            columns = connection.execute(
                f'PRAGMA table_info("{table}")'
            ).fetchall()

            foreign_keys = connection.execute(
                f'PRAGMA foreign_key_list("{table}")'
            ).fetchall()

            fk_columns = {
                row[3]: f"{row[2]}.{row[4]}"
                for row in foreign_keys
            }

            lines.append(
                "| Field | Data Type | Required | "
                "Primary Key | Foreign Key | Default |"
            )
            lines.append(
                "|---|---|---|---|---|---|"
            )

            for column in columns:
                _, name, data_type, not_null, default, pk = column

                required = "Yes" if not_null or pk else "No"
                primary = "Yes" if pk else "No"
                foreign = fk_columns.get(name, "-")
                default_value = (
                    str(default) if default is not None else "-"
                )

                lines.append(
                    f"| {name} | {data_type} | {required} | "
                    f"{primary} | {foreign} | {default_value} |"
                )

            lines.append("")

        output_path = DOCS_DIR / "data_dictionary.md"
        output_path.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

        print("Data dictionary generated successfully!")
        print(f"Tables documented: {len(tables)}")
        print(f"Saved to: {output_path}")

    finally:
        connection.close()


if __name__ == "__main__":
    generate_data_dictionary()