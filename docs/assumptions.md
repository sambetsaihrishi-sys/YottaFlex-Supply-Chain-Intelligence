# Project Assumptions and Limitations

## Dataset Assumptions

1. Random seed: 20261022.
2. Baseline contains 3,000 SKUs.
3. There are 50 locations and 500 suppliers.
4. Each SKU is assigned to three demand locations.
5. Demand covers 52 weeks in 2026.
6. Inventory is initialized before the planning period.
7. Supplier capacity is measured in units per week.
8. Lead time is measured in calendar days.

## Inventory Assumptions

Projected balance is calculated as:

Closing Balance = Opening Balance + Inbound - Demand

Negative balances represent outstanding backlog.
Purchase orders are counted using revised delivery dates.
Physical receipt confirmation is not fully implemented.

## Shortage Assumptions

Shortages represent increases in outstanding backlog.
Severity is based on newly unmet demand relative to demand.
Shortage causes are preliminary classifications.

## Mitigation Assumptions

Only approved supplier relationships are evaluated.
Options consider capacity, MOQ, lead time, and cost.
Candidate feasibility is evaluated independently.
Multiple options do not collectively reserve capacity.

## Production Assumptions

Industrial-category SKUs are treated as finished goods.
Other SKU categories can be BOM components.
Production capacity is defined weekly.
Component availability checks are preliminary.
Cumulative component consumption is not fully implemented.
Completed production receipts are not included in planning.

## Anomaly Assumptions

Five controlled anomaly cases are generated.
Ground-truth labels are stored separately.
The initial evaluation has only positive anomaly examples.
Reported accuracy is not a real-world performance estimate.

## Limitations

- No live supplier or warehouse integrations.
- Demand forecasts are synthetic, not ML-generated.
- Shortage severity distribution is highly imbalanced.
- Mitigation feasibility is preliminary.
- Production feasibility is preliminary.
- The dashboard is a local prototype.
- Some cross-table validations remain incomplete.
