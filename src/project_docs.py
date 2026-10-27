import sqlite3
from pathlib import Path

DOCS_DIR = Path("docs")
DB_PATH = Path("data/supply_chain.db")


def generate_project_docs():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    architecture_lines = [
        "# System Architecture",
        "",
        "## Project Overview",
        "",
        "The Supply Chain Intelligence System is a Python-based,",
        "rule-driven decision-support application.",
        "",
        "It connects forecast demand, inventory, supplier capacity,",
        "lead times, production planning, and shortage mitigation.",
        "",
        "## System Workflow",
        "",
        "1. Synthetic Data Generation",
        "2. Master Data and Transaction Records",
        "3. SQLite Relational Database",
        "4. Inventory Planning Engine",
        "5. Shortage Detection Engine",
        "6. Supplier Mitigation Engine",
        "7. Streamlit Dashboard",
        "",
        "## Main Components",
        "",
        "### Data Generator",
        "Creates deterministic synthetic supply chain datasets.",
        "",
        "### Database",
        "Stores related entities using primary keys and foreign keys.",
        "",
        "### Inventory Engine",
        "Calculates weekly projected inventory balances.",
        "",
        "### Shortage Engine",
        "Identifies additional unmet demand and assigns severity.",
        "",
        "### Mitigation Engine",
        "Evaluates suppliers using capacity, MOQ, lead time, and cost.",
        "",
        "### Production Engine",
        "Generates production plans, factory capacity, and BOM records.",
        "",
        "### Production Validation",
        "Checks capacity and preliminary component availability.",
        "",
        "### Anomaly Detection",
        "Evaluates five demonstration supply chain exceptions.",
        "",
        "### Event History",
        "Records purchase-order status transitions.",
        "",
        "### Dashboard",
        "Displays supply chain metrics and planning results.",
        "",
        "## Technology Stack",
        "",
        "- Python",
        "- Pandas",
        "- NumPy",
        "- SQLite",
        "- Streamlit",
        "- Plotly",
        "- Pytest",
        "",
        "## Design Decisions",
        "",
        "- Synthetic datasets use seed 20261022.",
        "- Inventory balances are calculated from source data.",
        "- Negative projected balances represent backlog.",
        "- Ground-truth labels are stored separately.",
        "- Production feasibility is preliminary.",
        "- Mitigation options are evaluated independently.",
    ]

    architecture_path = DOCS_DIR / "architecture.md"

    architecture_path.write_text(
        "\n".join(architecture_lines) + "\n",
        encoding="utf-8"
    )

    assumptions_lines = [
        "# Project Assumptions and Limitations",
        "",
        "## Dataset Assumptions",
        "",
        "1. Random seed: 20261022.",
        "2. Baseline contains 3,000 SKUs.",
        "3. There are 50 locations and 500 suppliers.",
        "4. Each SKU is assigned to three demand locations.",
        "5. Demand covers 52 weeks in 2026.",
        "6. Inventory is initialized before the planning period.",
        "7. Supplier capacity is measured in units per week.",
        "8. Lead time is measured in calendar days.",
        "",
        "## Inventory Assumptions",
        "",
        "Projected balance is calculated as:",
        "",
        "Closing Balance = Opening Balance + Inbound - Demand",
        "",
        "Negative balances represent outstanding backlog.",
        "Purchase orders are counted using revised delivery dates.",
        "Physical receipt confirmation is not fully implemented.",
        "",
        "## Shortage Assumptions",
        "",
        "Shortages represent increases in outstanding backlog.",
        "Severity is based on newly unmet demand relative to demand.",
        "Shortage causes are preliminary classifications.",
        "",
        "## Mitigation Assumptions",
        "",
        "Only approved supplier relationships are evaluated.",
        "Options consider capacity, MOQ, lead time, and cost.",
        "Candidate feasibility is evaluated independently.",
        "Multiple options do not collectively reserve capacity.",
        "",
        "## Production Assumptions",
        "",
        "Industrial-category SKUs are treated as finished goods.",
        "Other SKU categories can be BOM components.",
        "Production capacity is defined weekly.",
        "Component availability checks are preliminary.",
        "Cumulative component consumption is not fully implemented.",
        "Completed production receipts are not included in planning.",
        "",
        "## Anomaly Assumptions",
        "",
        "Five controlled anomaly cases are generated.",
        "Ground-truth labels are stored separately.",
        "The initial evaluation has only positive anomaly examples.",
        "Reported accuracy is not a real-world performance estimate.",
        "",
        "## Limitations",
        "",
        "- No live supplier or warehouse integrations.",
        "- Demand forecasts are synthetic, not ML-generated.",
        "- Shortage severity distribution is highly imbalanced.",
        "- Mitigation feasibility is preliminary.",
        "- Production feasibility is preliminary.",
        "- The dashboard is a local prototype.",
        "- Some cross-table validations remain incomplete.",
    ]

    assumptions_path = DOCS_DIR / "assumptions.md"

    assumptions_path.write_text(
        "\n".join(assumptions_lines) + "\n",
        encoding="utf-8"
    )

    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run python -m src.database first."
        )

    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        tables = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' "
            "AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()

        schema_lines = [
            "# Database Schema",
            "",
            "## Overview",
            "",
            "This document describes the SQLite database structure.",
            "",
            "## Tables and Relationships",
            ""
        ]

        for (table_name,) in tables:
            schema_lines.append(f"## {table_name}")
            schema_lines.append("")

            columns = connection.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

            schema_lines.append(
                "| Column | Type | Primary Key | Required |"
            )
            schema_lines.append(
                "|---|---|---|---|"
            )

            for column in columns:
                _, name, dtype, not_null, _, pk = column

                primary = "Yes" if pk else "No"
                required = "Yes" if not_null or pk else "No"

                schema_lines.append(
                    f"| {name} | {dtype} | {primary} | {required} |"
                )

            schema_lines.append("")
            schema_lines.append("### Foreign Keys")
            schema_lines.append("")

            foreign_keys = connection.execute(
                f'PRAGMA foreign_key_list("{table_name}")'
            ).fetchall()

            if foreign_keys:
                for fk in foreign_keys:
                    schema_lines.append(
                        f"- `{fk[3]}` references `{fk[2]}.{fk[4]}`"
                    )
            else:
                schema_lines.append("- None")

            schema_lines.append("")

        schema_path = DOCS_DIR / "schema.md"

        schema_path.write_text(
            "\n".join(schema_lines) + "\n",
            encoding="utf-8"
        )

        print("\n========== DOCUMENTATION GENERATION ==========")
        print("Architecture documentation generated.")
        print("Assumptions documentation generated.")
        print(f"Database schema documented: {len(tables)} tables.")
        print("\nFiles saved:")
        print("docs/architecture.md")
        print("docs/assumptions.md")
        print("docs/schema.md")

    finally:
        connection.close()


if __name__ == "__main__":
    generate_project_docs()