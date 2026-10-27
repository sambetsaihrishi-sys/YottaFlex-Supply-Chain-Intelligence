# Validation Report

Generated at (UTC): 2026-10-27T09:17:21.864569+00:00

Database tables: 15

Total checks: 12
Passed: 12
Failed: 0

## Validation Results

| Validation | Result |
|---|---|
| Required CSV files exist | PASS |
| Inventory balance reconciles | PASS |
| Projected balance reconciles | PASS |
| Shortage IDs are unique | PASS |
| Shortage quantities are positive | PASS |
| Mitigation IDs are unique | PASS |
| Individual mitigation capacity respected | PASS |
| Purchase order IDs are unique | PASS |
| Purchase order quantities are positive | PASS |
| Production plan IDs are unique | PASS |
| Production capacity IDs are unique | PASS |
| SQLite foreign keys valid | PASS |

## Scope and Limitations

These checks cover baseline integrity and arithmetic.

They do not prove complete production feasibility,
collective mitigation capacity allocation,
or comprehensive lifecycle correctness.

Additional business-rule testing is required.
