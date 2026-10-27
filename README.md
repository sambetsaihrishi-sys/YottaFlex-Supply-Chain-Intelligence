# Supply Chain Intelligence System

### YottaFlex AI — 72-Hour Code Challenge

A Python-based supply chain decision-support system that matches forecast demand with inventory, supplier capacity, lead times, and production constraints to identify and prioritize shortages.

The project uses deterministic synthetic data generation, rule-based inventory planning, shortage detection, mitigation recommendations, and an interactive Streamlit dashboard.

## 1. Project Objective

The objective is to help supply chain planners answer three questions:

1. Will available inventory meet forecast demand?
2. Which products and locations face shortages?
3. What mitigation options could reduce those shortages?

The application provides traceable records and preliminary decision-support outputs.

## 2. Technology Stack

- Python
- Pandas
- NumPy
- SQLite
- Streamlit
- Plotly
- Pytest

## 3. Dataset Overview

The full synthetic dataset uses the following configuration:

| Dataset | Records |
|---|---:|
| SKUs | 3,000 |
| Locations | 50 |
| Suppliers | 500 |
| Weekly demand forecasts | 468,000 |
| Initial inventory records | 9,000 |
| Supplier-SKU relationships | 6,000 |
| Supplier capacity records | 312,000 |
| Lead-time records | 6,000 |
| Purchase orders | 10,000 |

Each SKU is assigned to three locations, with demand generated for 52 weeks.

The fixed random seed is `20261022`.

## 4. System Architecture

The application follows this workflow:

```text
Synthetic Data Generator
          |
          v
Master Data and Transactions
          |
          v
SQLite Database
          |
          v
Inventory Planning Engine
          |
          v
Shortage Detection
          |
          v
Mitigation Recommendation Engine
          |
          v
Streamlit Dashboard
```

Production planning, anomaly detection, validation, and event-history modules provide additional functionality.

## 5. Features

### Synthetic Data Generation

Generates products, locations, suppliers, inventory, demand forecasts, supplier capacities, lead times, and purchase orders.

### Inventory Planning

Calculates weekly projected inventory balances.

Formula:

```text
Closing Balance = Opening Balance + Incoming Supply - Forecast Demand
```

Negative projected balances represent outstanding demand under the backlog assumption.

### Shortage Detection

Identifies additional unmet demand and classifies shortages using severity thresholds.

### Mitigation Recommendations

Evaluates candidate supplier options using:

- Supplier approval
- Available capacity
- Minimum order quantities
- Delivery lead times
- Estimated costs
- Shortage coverage

Recommendations are preliminary and are not collectively reserved against supplier capacity.

### Production Planning

Generates BOM relationships, production capacity, and production plans.

Preliminary feasibility checks compare production requirements against available component inventory.

### Anomaly Detection

Includes demonstration scenarios for:

1. Duplicate inbound counting
2. Unapproved substitution
3. Supplier capacity exceedance
4. Ignored lead times
5. Units-of-measure mismatch

Ground-truth labels are stored separately from detection results.

### Event History

Records synthetic purchase-order status transitions and preserves their history in SQLite.

### Interactive Dashboard

Provides views for demand, inventory, shortages, mitigation options, and production planning.

## 6. Installation

Python 3.14.3 was used during development.

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd YottaFlex-Supply-Chain-Intelligence
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 7. Generate Data

Run:

```bash
python -m src.data_generator
```

Generate production data:

```bash
python -m src.production_engine
```

## 8. Run Planning Modules

Execute these commands in order:

```bash
python -m src.inventory_engine
python -m src.shortage_engine
python -m src.mitigation_engine
python -m src.production_validation
```

## 9. Initialize Database

Run:

```bash
python -m src.database
python -m src.database_extension
python -m src.event_history
```

The current database loader is intended for fresh development databases. Repeated imports require additional handling to avoid duplicate primary keys.

## 10. Run Anomaly Evaluation

```bash
python -m src.anomaly_generator
python -m src.anomaly_detector
python -m src.anomaly_evaluation
```

The initial anomaly evaluation includes five deliberately constructed negative scenarios. Its accuracy should not be interpreted as performance on unseen operational data.

## 11. Launch Dashboard

```bash
python -m streamlit run app.py
```

Open:

http://localhost:8501

## 12. Run Automated Tests

```bash
python -m pytest tests/ -v
```

## 13. Validate Data

```bash
python -m src.validation
```

## 14. Reproducibility

The generator uses a fixed seed.

Run:

```bash
python -m src.reproducibility
```

The reproducibility module regenerates the nine baseline datasets twice and compares their row counts and SHA-256 checksums.

## 15. Assumptions and Limitations

- The application uses synthetic data, not real supplier information.
- Each SKU is assigned to three demand locations.
- Forecast demand is synthetically generated rather than predicted by a trained ML model.
- Negative inventory balances represent carried-forward backlog.
- The mitigation engine evaluates supplier options independently.
- Production feasibility does not yet enforce cumulative component consumption.
- Anomaly evaluation currently uses a limited demonstration dataset.
- Purchase-order events are simulated rather than sourced from an external operational system.
- Production receipts are not yet integrated into the main projected inventory calculation.

## 16. Data Provenance

The baseline datasets are generated synthetically using Python and NumPy.

No confidential supplier, customer, or personal information is required.

## 17. AI Assistance Disclosure

AI tools were used to assist with implementation, debugging, explanations, and documentation.

Prompt history is maintained in:

`prompts/prompt_history.md`

The project should be reviewed and validated by its author before submission.

## 18. Project Status

This repository contains an executable supply chain planning prototype.

The documented limitations identify functionality that requires further development before production use.