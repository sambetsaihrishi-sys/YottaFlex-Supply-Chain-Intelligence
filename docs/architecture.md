# System Architecture

## Project Overview

The Supply Chain Intelligence System is a Python-based,
rule-driven decision-support application.

It connects forecast demand, inventory, supplier capacity,
lead times, production planning, and shortage mitigation.

## System Workflow

1. Synthetic Data Generation
2. Master Data and Transaction Records
3. SQLite Relational Database
4. Inventory Planning Engine
5. Shortage Detection Engine
6. Supplier Mitigation Engine
7. Streamlit Dashboard

## Main Components

### Data Generator
Creates deterministic synthetic supply chain datasets.

### Database
Stores related entities using primary keys and foreign keys.

### Inventory Engine
Calculates weekly projected inventory balances.

### Shortage Engine
Identifies additional unmet demand and assigns severity.

### Mitigation Engine
Evaluates suppliers using capacity, MOQ, lead time, and cost.

### Production Engine
Generates production plans, factory capacity, and BOM records.

### Production Validation
Checks capacity and preliminary component availability.

### Anomaly Detection
Evaluates five demonstration supply chain exceptions.

### Event History
Records purchase-order status transitions.

### Dashboard
Displays supply chain metrics and planning results.

## Technology Stack

- Python
- Pandas
- NumPy
- SQLite
- Streamlit
- Plotly
- Pytest

## Design Decisions

- Synthetic datasets use seed 20261022.
- Inventory balances are calculated from source data.
- Negative projected balances represent backlog.
- Ground-truth labels are stored separately.
- Production feasibility is preliminary.
- Mitigation options are evaluated independently.
