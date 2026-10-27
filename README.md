# YottaFlex Supply Chain Intelligence System

### AI Forward Deployed Engineer — 72-Hour Code Challenge

A Python-based supply chain decision-support system designed to identify inventory shortages, evaluate supplier constraints, generate mitigation recommendations, and support production planning.

The project combines **synthetic data generation, inventory forecasting, shortage detection, supplier capacity allocation, production feasibility analysis, anomaly detection, and an interactive Streamlit dashboard**.

**GitHub Repository:**
https://github.com/sambetsaihrishi-sys/YottaFlex-Supply-Chain-Intelligence

---

## 1. Project Overview

Supply chains involve multiple interconnected factors, including customer demand, available inventory, supplier production capacity, delivery lead times, purchase orders, and manufacturing constraints.

When these factors are not evaluated together, businesses may experience:

* Inventory shortages
* Delayed customer deliveries
* Excessive supplier commitments
* Production delays
* Incorrect inventory calculations
* Unreliable mitigation recommendations

The **YottaFlex Supply Chain Intelligence System** provides an integrated prototype for analyzing these challenges.

The system uses deterministic synthetic datasets and rule-based decision engines to produce explainable planning outputs.

### Main Objectives

1. Compare forecast demand with available inventory.
2. Identify potential inventory shortages.
3. Prioritize shortages according to severity.
4. Evaluate possible supplier mitigation options.
5. Allocate supplier capacity across competing recommendations.
6. Analyze production requirements using bill-of-materials relationships.
7. Detect predefined supply chain anomalies.
8. Generate reproducible datasets and validation reports.
9. Visualize planning results through an interactive dashboard.

---

## 2. Technology Stack

| Technology | Purpose                      |
| ---------- | ---------------------------- |
| Python     | Application development      |
| Pandas     | Data processing and analysis |
| NumPy      | Synthetic data generation    |
| SQLite     | Relational data storage      |
| Streamlit  | Interactive dashboard        |
| Plotly     | Data visualization           |
| Pytest     | Automated testing            |
| Git        | Version control              |
| GitHub     | Project repository           |
| JSON / CSV | Data exchange and reporting  |
| SHA-256    | Reproducibility verification |

**Development environment:** Python 3.14.3 on Windows.

Package versions used during development are recorded in `requirements.txt`.

---

## 3. Synthetic Dataset Overview

The project generates a large synthetic supply chain dataset using a fixed random seed.

**Random Seed:** `20261022`

**Planning Year:** `2026`

### Baseline Data

| Dataset                    | Record Count |
| -------------------------- | -----------: |
| SKUs                       |        3,000 |
| Locations                  |           50 |
| Suppliers                  |          500 |
| Forecast Demand            |      468,000 |
| Initial Inventory          |        9,000 |
| Supplier-SKU Relationships |        6,000 |
| Supplier Capacity          |      312,000 |
| Supplier Lead Times        |        6,000 |
| Purchase Orders            |       10,000 |

The demand dataset covers 52 planning weeks.

Each SKU is assigned to three demand locations.

### Additional Generated Outputs

| Dataset                       | Record Count |
| ----------------------------- | -----------: |
| BOM Relationships             |          278 |
| Production Plans              |        7,228 |
| Production Capacity Records   |        7,228 |
| Projected Inventory Records   |      468,000 |
| Shortage Records              |      402,296 |
| Mitigation Options            |      804,592 |
| Proposed Capacity Allocations |       99,173 |
| Component Requirement Records |       14,456 |

These figures correspond to the documented full-scale generation configuration.

Actual results should be verified after running the generation pipeline.

All data is synthetic and is intended for demonstration and evaluation.

---

## 4. System Architecture

The system follows a modular architecture.

```text
                  SYNTHETIC DATA GENERATOR
                             |
                             v
                 MASTER AND TRANSACTION DATA
                             |
              +--------------+--------------+
              |                             |
              v                             v
       SQLITE DATABASE              INVENTORY ENGINE
              |                             |
              v                             v
       EVENT HISTORY                PROJECTED INVENTORY
                                            |
                                            v
                                     SHORTAGE ENGINE
                                            |
                                            v
                                    MITIGATION ENGINE
                                            |
                                            v
                                   CAPACITY ALLOCATOR
                                            |
                                            v
                                  ALLOCATION VALIDATION


                PRODUCTION PLANNING ENGINE
                             |
                             v
                      BOM REQUIREMENTS
                             |
                             v
                     MATERIAL ALLOCATOR
                             |
                             v
                  PRODUCTION FEASIBILITY


                   ANOMALY GENERATOR
                             |
                             v
                     ANOMALY DETECTOR
                             |
                             v
                    EVALUATION METRICS


                    STREAMLIT DASHBOARD
                             |
                             v
                   VISUALIZATION & ANALYSIS
```

Each processing module has a defined responsibility.

The outputs from these modules provide traceable information for evaluating supply chain conditions.

---

## 5. Core Features

### 5.1 Synthetic Data Generation

The data generator creates interconnected supply chain records, including:

* Products and SKU identifiers
* Warehouse and factory locations
* Suppliers
* Supplier-product relationships
* Forecast demand
* Initial inventory
* Weekly supplier capacities
* Supplier lead times
* Purchase orders
* Delivery delays

The generator uses a fixed seed to support reproducibility.

**Main module:**

`src/data_generator.py`

### 5.2 Inventory Planning Engine

The inventory engine calculates projected inventory balances for each SKU, location, and planning week.

**Inventory Calculation:**

```text
Closing Inventory =
Opening Inventory + Incoming Supply - Forecast Demand
```

When projected inventory becomes negative, the system interprets the negative quantity as outstanding demand under its backlog assumption.

**Output:**

`data/projected_inventory.csv`

**Main module:**

`src/inventory_engine.py`

### 5.3 Shortage Detection Engine

The shortage engine analyzes projected inventory to identify additional unmet demand.

Shortages are assigned severity categories:

* CRITICAL
* HIGH
* MEDIUM
* LOW

These categories help planners prioritize which shortages require attention.

The engine distinguishes newly generated shortage quantities from backlog carried over from previous weeks.

**Output:**

`data/shortage.csv`

**Main module:**

`src/shortage_engine.py`

**Limitation:** Shortage causes and severity are generated using predefined heuristic rules. They have not been calibrated against real operational data.

### 5.4 Mitigation Recommendation Engine

The mitigation engine evaluates supplier options for addressing identified shortages.

The evaluation considers:

* Supplier approval
* Supplier-product relationships
* Remaining supplier capacity
* Minimum order quantities
* Supplier lead times
* Required shortage quantities
* Estimated purchase costs

The system produces candidate recommendations and identifies options that satisfy its preliminary feasibility checks.

**Output:**

`data/mitigation_option.csv`

**Main module:**

`src/mitigation_engine.py`

**Limitation:** Initial mitigation feasibility is assessed independently. It does not guarantee that multiple recommendations can all be fulfilled simultaneously.

### 5.5 Supplier Capacity Allocation

The capacity allocation module addresses competition between mitigation recommendations for the same supplier capacity.

The system:

1. Loads feasible mitigation candidates.
2. Calculates capacity remaining after existing purchase-order commitments.
3. Prioritizes shortage recommendations.
4. Allocates supplier capacity to selected recommendations.
5. Reduces remaining capacity after each allocation.
6. Produces proposed allocation records.

The algorithm follows a **greedy allocation approach**.

**Output:**

`data/capacity_allocation.csv`

**Main module:**

`src/capacity_allocator.py`

The documented dataset contains:

* **99,173 proposed allocations**
* **15,883,282 allocated units**

These allocations are planning proposals, not confirmed purchase orders.

The greedy algorithm does not guarantee a globally optimal solution and currently selects at most one supplier option per shortage.

### 5.6 Supplier Capacity Validation

The allocation validation module checks whether supplier capacity is exceeded after considering existing purchase-order commitments and proposed allocations.

**Validation Rule:**

```text
Existing PO Commitments + Proposed Allocations
<=
Available Supplier Capacity
```

The validation is performed for supplier-product relationships and planning weeks.

**Output:**

`data/allocation_validation.csv`

**Main module:**

`src/allocation_validation.py`

The validation results must be reviewed before interpreting allocations as capacity-feasible recommendations.

### 5.7 Production Planning

The production engine generates manufacturing-related records, including:

* Bill of materials
* Production plans
* Factory production capacities
* Component requirements

These records connect finished products with their manufacturing components.

**Main module:**

`src/production_engine.py`

**Related module:**

`src/production_validation.py`

### 5.8 Cumulative Material Allocation

The material allocation module evaluates whether production plans can be fulfilled with available components.

It processes production plans in chronological order.

For each plan, the engine:

1. Identifies required BOM components.
2. Checks available component inventory.
3. Considers eligible inbound purchase orders.
4. Checks the production capacity limit.
5. Calculates feasible manufacturing quantity.
6. Deducts consumed components.
7. Classifies the production result.

The supported classifications are:

| Status   | Meaning                                 |
| -------- | --------------------------------------- |
| FEASIBLE | Entire planned quantity can be produced |
| PARTIAL  | Only part of the plan can be produced   |
| BLOCKED  | No production quantity can be allocated |

**Output:**

`data/material_allocation.csv`

**Main module:**

`src/material_allocator.py`

**Limitations:** This module does not yet model manufacturing completion lead times, all BOM effective dates, or finished-goods receipts in the main inventory projection.

### 5.9 Anomaly Detection

The project includes rule-based anomaly detection for five predefined supply chain scenarios.

**Anomaly Scenarios:**

1. Duplicate inbound inventory counting
2. Unapproved product substitution
3. Supplier capacity exceedance
4. Shortage calculations that ignore lead times
5. Units-of-measure mismatch

The implementation includes synthetic anomaly examples, detection logic, and evaluation scripts.

**Main modules:**

```text
src/anomaly_generator.py
src/anomaly_detector.py
src/anomaly_evaluation.py
src/anomaly_test_cases.py
src/evaluation_detector.py
src/evaluation_metrics.py
```

The evaluation calculates classification metrics, including:

* True positives
* True negatives
* False positives
* False negatives
* Accuracy
* Precision
* Recall
* F1 score
* False-positive rate

Ground-truth labels are stored separately from the evaluation inputs.

**Limitation:** The anomaly tests use a small synthetic demonstration dataset. High performance on these examples does not establish performance on unseen real-world anomalies.

### 5.10 Purchase Order Event History

The event-history module records synthetic purchase-order lifecycle events.

Example states include:

```text
CREATED
   |
   v
CONFIRMED
   |
   v
DELAYED
```

The module demonstrates historical record tracking for supplier transactions.

**Main module:**

`src/event_history.py`

**Limitation:** Events are simulated and do not constitute a complete production-grade purchase-order state machine.

### 5.11 SQLite Database

The project uses SQLite for relational storage.

The database contains tables representing key supply chain entities and derived planning outputs.

These include:

* SKU
* Location
* Supplier
* Forecast Demand
* Inventory
* Supplier-SKU
* Supplier Capacity
* Lead Time
* Purchase Order
* BOM
* Production Capacity
* Production Plan
* Shortage
* Mitigation Option
* Purchase Order Event History

The implementation includes primary-key and foreign-key constraints for supported relationships.

**Database Modules:**

```text
src/database.py
src/database_extension.py
src/event_history.py
```

The database file is generated locally and excluded from Git using `.gitignore`.

### 5.12 Interactive Streamlit Dashboard

The project includes an interactive dashboard developed using Streamlit and Plotly.

The dashboard provides six primary views:

| Dashboard Tab | Purpose                                  |
| ------------- | ---------------------------------------- |
| Overview      | Summary of supply chain records and KPIs |
| Demand        | Forecast demand analysis                 |
| Inventory     | Projected inventory analysis             |
| Shortage      | Shortage identification and severity     |
| Mitigation    | Supplier mitigation recommendations      |
| Production    | Production planning information          |

**Application File:**

`app.py`

---

## 6. Project Structure

```text
YottaFlex-Supply-Chain-Intelligence/
|
|-- app.py
|-- run_pipeline.py
|-- README.md
|-- requirements.txt
|-- .gitignore
|
|-- src/
|   |-- __init__.py
|   |-- data_generator.py
|   |-- inventory_engine.py
|   |-- shortage_engine.py
|   |-- mitigation_engine.py
|   |-- capacity_allocator.py
|   |-- allocation_validation.py
|   |-- production_engine.py
|   |-- production_validation.py
|   |-- material_allocator.py
|   |-- anomaly_generator.py
|   |-- anomaly_detector.py
|   |-- anomaly_evaluation.py
|   |-- anomaly_test_cases.py
|   |-- evaluation_detector.py
|   |-- evaluation_metrics.py
|   |-- database.py
|   |-- database_extension.py
|   |-- event_history.py
|   |-- validation.py
|   |-- validation_report.py
|   |-- reproducibility.py
|   |-- documentation_generator.py
|   |-- project_docs.py
|
|-- data/
|   |-- source_manifest.json
|   |-- sample/
|   |-- anomalies/
|
|-- docs/
|   |-- architecture.md
|   |-- assumptions.md
|   |-- schema.md
|   |-- data_dictionary.md
|   |-- validation_report.md
|   |-- validation_summary.json
|   |-- reproducibility_report.json
|   |-- anomaly_metrics.json
|   |-- ai_usage.md
|
|-- prompts/
|   |-- prompt_history.md
|
|-- tests/
|   |-- test_generator.py
|   |-- test_inventory.py
|   |-- test_shortages.py
|   |-- test_validation.py
```

Generated CSV outputs and the local SQLite database are not included in the full Git repository.

Representative sample files are provided in `data/sample/`.

---

## 7. Installation Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/sambetsaihrishi-sys/YottaFlex-Supply-Chain-Intelligence.git
```

Navigate to the project directory:

```bash
cd YottaFlex-Supply-Chain-Intelligence
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 3: Activate the Virtual Environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

---

## 8. Generate Synthetic Data

Generate the baseline supply chain datasets:

```bash
python -m src.data_generator
```

Generate production-related datasets:

```bash
python -m src.production_engine
```

This creates the foundational CSV files required by the planning modules.

---

## 9. Execute Supply Chain Planning

Run the following commands in order.

### Inventory Planning

```bash
python -m src.inventory_engine
```

### Shortage Detection

```bash
python -m src.shortage_engine
```

### Mitigation Recommendation Generation

```bash
python -m src.mitigation_engine
```

### Production Feasibility Validation

```bash
python -m src.production_validation
```

### Supplier Capacity Allocation

```bash
python -m src.capacity_allocator
```

### Supplier Allocation Validation

```bash
python -m src.allocation_validation
```

### Cumulative Production Material Allocation

```bash
python -m src.material_allocator
```

These commands generate planning outputs in the `data/` directory.

---

## 10. Initialize the SQLite Database

Run the database initialization modules after generating the underlying CSV data.

```bash
python -m src.database
```

```bash
python -m src.database_extension
```

```bash
python -m src.event_history
```

The database is stored locally at:

```text
data/supply_chain.db
```

**Important:** These loaders are intended for a fresh development database. Existing database files should be backed up before rebuilding. Repeated imports may cause duplicate-key errors.

---

## 11. Run Anomaly Detection

Generate demonstration anomaly scenarios:

```bash
python -m src.anomaly_generator
```

Run anomaly detection:

```bash
python -m src.anomaly_detector
```

Evaluate the demonstration cases:

```bash
python -m src.anomaly_evaluation
```

Generate additional evaluation cases:

```bash
python -m src.anomaly_test_cases
```

Run the evaluation detector:

```bash
python -m src.evaluation_detector
```

Calculate evaluation metrics:

```bash
python -m src.evaluation_metrics
```

The evaluation uses synthetic labeled examples and should not be interpreted as a benchmark on real operational data.

---

## 12. Run the Automated Pipeline

The project includes an automated execution script.

```bash
python run_pipeline.py
```

This script executes the core generation, planning, allocation, anomaly detection, and testing modules in dependency order.

If a module exits with an error, pipeline execution stops.

**Important:** The current pipeline does not automatically rebuild the SQLite database or regenerate every documentation report.

Use the separate database initialization and documentation commands where required.

---

## 13. Launch the Streamlit Dashboard

After generating the required datasets, run:

```bash
python -m streamlit run app.py
```

Open the application in your browser:

```text
http://localhost:8501
```

The dashboard provides interactive views of demand, inventory, shortages, mitigation options, and production planning.

---

## 14. Automated Testing

The project includes unit tests for the data generator, inventory calculations, shortage detection, and selected validation rules.

Run the tests using:

```bash
python -m pytest tests/ -v
```

For compact output:

```bash
python -m pytest tests/ -q
```

Automated tests help identify regressions and verify selected data-processing rules.

Passing the current tests does not establish complete business-rule coverage.

---

## 15. Data Validation

The project includes validation routines for generated data.

These cover selected checks involving:

* Record uniqueness
* Required relationships
* Referential integrity
* Data consistency
* Quantity validity
* Supplier capacity
* Production feasibility

Execute:

```bash
python -m src.validation
```

Generate the validation report:

```bash
python -m src.validation_report
```

Outputs include:

```text
docs/validation_report.md
docs/validation_summary.json
```

Allocation-specific results are also available in:

```text
data/allocation_validation.csv
```

These reports should be reviewed before treating the generated planning results as validated.

---

## 16. Reproducibility Verification

Reproducibility is supported through deterministic synthetic data generation.

**Configured Seed:** `20261022`

Run:

```bash
python -m src.reproducibility
```

The reproducibility script executes the configured generation modules twice.

It then compares **26 generated datasets and outputs** using:

1. Record counts
2. SHA-256 file checksums

The results are saved to:

```text
docs/reproducibility_report.json
```

If all tracked outputs match, the report records a successful reproducibility result.

This confirms deterministic file generation for the checked configuration, not the correctness of every business rule.

**Note:** The reproducibility script regenerates CSV outputs but does not automatically rebuild the SQLite database.

---

## 17. Data Documentation

The project includes supporting technical documentation.

| Document                           | Description                         |
| ---------------------------------- | ----------------------------------- |
| `docs/architecture.md`             | System architecture                 |
| `docs/schema.md`                   | Relational data model               |
| `docs/data_dictionary.md`          | Dataset fields and structure        |
| `docs/assumptions.md`              | Planning assumptions                |
| `docs/validation_report.md`        | Data validation results             |
| `docs/validation_summary.json`     | Machine-readable validation summary |
| `docs/reproducibility_report.json` | Reproducibility evidence            |
| `docs/anomaly_metrics.json`        | Anomaly evaluation metrics          |
| `docs/ai_usage.md`                 | AI assistance disclosure            |
| `prompts/prompt_history.md`        | AI interaction history              |

The documents describe the prototype design and provide supporting review information.

---

## 18. Data Provenance

All baseline supply chain datasets are generated synthetically.

The project does not require real supplier, customer, employee, or confidential business records.

The source manifest is available at:

```text
data/source_manifest.json
```

The manifest records:

* Project identification
* Synthetic data source
* Generator module
* Random seed
* Planning year
* Baseline dataset configuration
* Data provenance

A small representative dataset is included in:

```text
data/sample/
```

These samples illustrate the data structure but are not intended to be a complete, referentially consistent miniature supply chain database.

---

## 19. AI Assistance Disclosure

ChatGPT was used to support parts of the development process, including:

* Interpreting project requirements
* Planning the system architecture
* Generating implementation suggestions
* Writing and refining Python modules
* Debugging errors
* Designing validation routines
* Producing documentation
* Explaining technical concepts

AI-generated suggestions require independent testing and verification.

The AI usage documentation is maintained at:

```text
docs/ai_usage.md
```

The prompt-history record is maintained at:

```text
prompts/prompt_history.md
```

The prompt-history file should contain the actual AI interactions used during development, rather than only a template or summary.

---

## 20. Assumptions

The prototype uses several simplifying assumptions.

1. Demand is generated synthetically for 52 planning weeks.
2. Each SKU is assigned to three demand locations.
3. Forecast demand is an input dataset rather than the output of a trained forecasting model.
4. Negative inventory represents outstanding demand carried forward.
5. Incoming supply is evaluated using recorded delivery dates.
6. Supplier capacity is represented at the supplier-product and weekly level.
7. Mitigation candidates are initially evaluated independently.
8. A separate greedy allocation algorithm distributes available supplier capacity.
9. Production feasibility depends on BOM requirements and available manufacturing components.
10. Purchase-order events represent simulated operational history.

These assumptions allow the system to demonstrate planning logic without requiring access to live enterprise systems.

---

## 21. Known Limitations

This implementation is a prototype and has several limitations.

### Forecasting

Demand is synthetically generated rather than predicted through a trained machine-learning model.

### Shortage Classification

Severity and shortage causes use simplified rules. The generated data produces a high proportion of critical shortages.

### Lead-Time Planning

Mitigation feasibility uses simplified order-placement and delivery assumptions. It does not provide complete forward scheduling of procurement decisions.

### Capacity Allocation

The greedy allocation algorithm does not guarantee globally optimal allocations.

It currently selects at most one supplier option per shortage and does not automatically convert proposed allocations into confirmed purchase orders.

### Production Planning

Cumulative component consumption is modeled, but manufacturing completion lead times and all BOM effective-date rules are not fully supported.

Finished production quantities are not integrated into the primary inventory projection.

### Anomaly Detection

Anomaly detection uses predefined rules and a small synthetic evaluation set.

The reported metrics do not demonstrate performance on unseen production data.

### Database

The SQLite implementation enforces selected relationships but does not represent every operational constraint.

### Dashboard

The Streamlit dashboard provides planning visualizations but is not a complete enterprise supply chain management application.

---

## 22. Future Improvements

Potential improvements include:

* Machine-learning-based demand forecasting
* More realistic inventory replenishment policies
* Supplier delivery reliability modeling
* Optimization-based shortage mitigation
* Multi-supplier allocation of individual shortages
* Full procurement lead-time scheduling
* Integration of production receipts into projected inventory
* BOM effective-date support
* Expanded anomaly datasets with stronger negative examples
* API integration with external ERP systems
* Interactive scenario simulations
* Additional end-to-end testing
* Deployment to a cloud platform

---

## 23. Project Results

The documented full-scale prototype generated:

| Metric                        |     Result |
| ----------------------------- | ---------: |
| Products                      |      3,000 |
| Locations                     |         50 |
| Suppliers                     |        500 |
| Demand Records                |    468,000 |
| Purchase Orders               |     10,000 |
| Shortage Records              |    402,296 |
| Mitigation Options            |    804,592 |
| Proposed Capacity Allocations |     99,173 |
| Proposed Allocated Units      | 15,883,282 |
| Production Plans              |      7,228 |

The system demonstrates how demand, inventory, procurement, supplier constraints, and production relationships can be combined into a traceable planning workflow.

The results are based on synthetic data and should not be interpreted as actual business performance.

---

## 24. Conclusion

The **YottaFlex Supply Chain Intelligence System** demonstrates an integrated approach to supply chain decision support.

It combines synthetic data generation, inventory planning, shortage identification, supplier mitigation recommendations, capacity allocation, manufacturing feasibility checks, anomaly detection, and interactive visualization.

The project emphasizes:

* Modular Python development
* Explainable business rules
* Data traceability
* Relational data modeling
* Automated testing
* Reproducibility
* Documentation of limitations

The current implementation is intended as a functional prototype that can be extended toward more advanced supply chain planning and optimization capabilities.

---

## 25. Repository

**Project:** YottaFlex Supply Chain Intelligence System

**Role:** AI Forward Deployed Engineer — Code Challenge

**GitHub:**

https://github.com/sambetsaihrishi-sys/YottaFlex-Supply-Chain-Intelligence

**Project Status:** Functional prototype with documented limitations.
