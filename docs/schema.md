# Database Schema

## Overview

This document describes the SQLite database structure.

## Tables and Relationships

## bom

| Column | Type | Primary Key | Required |
|---|---|---|---|
| bom_id | TEXT | Yes | Yes |
| parent_sku_id | TEXT | No | Yes |
| component_sku_id | TEXT | No | Yes |
| quantity_per_unit | INTEGER | No | Yes |
| effective_from | TEXT | No | Yes |
| effective_to | TEXT | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- `component_sku_id` references `sku.sku_id`
- `parent_sku_id` references `sku.sku_id`

## forecast_demand

| Column | Type | Primary Key | Required |
|---|---|---|---|
| demand_id | TEXT | Yes | Yes |
| sku_id | TEXT | No | Yes |
| location_id | TEXT | No | Yes |
| week | TEXT | No | Yes |
| forecast_qty | INTEGER | No | Yes |
| demand_spike | INTEGER | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- `location_id` references `location.location_id`
- `sku_id` references `sku.sku_id`

## inventory

| Column | Type | Primary Key | Required |
|---|---|---|---|
| inventory_id | TEXT | Yes | Yes |
| sku_id | TEXT | No | Yes |
| location_id | TEXT | No | Yes |
| snapshot_date | TEXT | No | Yes |
| on_hand_qty | INTEGER | No | Yes |
| reserved_qty | INTEGER | No | Yes |
| available_qty | INTEGER | No | Yes |
| unit_of_measure | TEXT | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- `location_id` references `location.location_id`
- `sku_id` references `sku.sku_id`

## lead_time

| Column | Type | Primary Key | Required |
|---|---|---|---|
| lead_time_id | TEXT | Yes | Yes |
| supplier_sku_id | TEXT | No | Yes |
| supplier_id | TEXT | No | Yes |
| sku_id | TEXT | No | Yes |
| lead_time_days | INTEGER | No | Yes |
| effective_from | TEXT | No | Yes |
| effective_to | TEXT | No | Yes |

### Foreign Keys

- `supplier_sku_id` references `supplier_sku.supplier_sku_id`

## location

| Column | Type | Primary Key | Required |
|---|---|---|---|
| location_id | TEXT | Yes | Yes |
| location_name | TEXT | No | Yes |
| city | TEXT | No | Yes |
| location_type | TEXT | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- None

## mitigation_option

| Column | Type | Primary Key | Required |
|---|---|---|---|
| mitigation_id | TEXT | Yes | Yes |
| shortage_id | TEXT | No | Yes |
| sku_id | TEXT | No | Yes |
| location_id | TEXT | No | Yes |
| supplier_id | TEXT | No | Yes |
| supplier_sku_id | TEXT | No | Yes |
| required_qty | INTEGER | No | Yes |
| proposed_qty | INTEGER | No | Yes |
| minimum_order_qty | INTEGER | No | Yes |
| remaining_capacity | INTEGER | No | Yes |
| lead_time_days | INTEGER | No | Yes |
| order_date | TEXT | No | Yes |
| arrival_date | TEXT | No | Yes |
| estimated_unit_cost | REAL | No | Yes |
| estimated_total_cost | REAL | No | Yes |
| coverage_ratio | REAL | No | Yes |
| on_time | INTEGER | No | Yes |
| feasible | INTEGER | No | Yes |
| recommendation_status | TEXT | No | Yes |

### Foreign Keys

- `supplier_sku_id` references `supplier_sku.supplier_sku_id`
- `supplier_id` references `supplier.supplier_id`
- `location_id` references `location.location_id`
- `sku_id` references `sku.sku_id`
- `shortage_id` references `shortage.shortage_id`

## production_capacity

| Column | Type | Primary Key | Required |
|---|---|---|---|
| production_capacity_id | TEXT | Yes | Yes |
| sku_id | TEXT | No | Yes |
| location_id | TEXT | No | Yes |
| week | TEXT | No | Yes |
| maximum_capacity | INTEGER | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- `location_id` references `location.location_id`
- `sku_id` references `sku.sku_id`

## production_plan

| Column | Type | Primary Key | Required |
|---|---|---|---|
| production_plan_id | TEXT | Yes | Yes |
| sku_id | TEXT | No | Yes |
| location_id | TEXT | No | Yes |
| week | TEXT | No | Yes |
| planned_qty | INTEGER | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- `location_id` references `location.location_id`
- `sku_id` references `sku.sku_id`

## purchase_order

| Column | Type | Primary Key | Required |
|---|---|---|---|
| po_id | TEXT | Yes | Yes |
| supplier_sku_id | TEXT | No | Yes |
| supplier_id | TEXT | No | Yes |
| sku_id | TEXT | No | Yes |
| location_id | TEXT | No | Yes |
| order_date | TEXT | No | Yes |
| expected_delivery_date | TEXT | No | Yes |
| revised_delivery_date | TEXT | No | Yes |
| quantity | INTEGER | No | Yes |
| unit_of_measure | TEXT | No | Yes |
| status | TEXT | No | Yes |
| transport_delayed | INTEGER | No | Yes |
| delay_days | INTEGER | No | Yes |

### Foreign Keys

- `location_id` references `location.location_id`
- `supplier_sku_id` references `supplier_sku.supplier_sku_id`

## purchase_order_event

| Column | Type | Primary Key | Required |
|---|---|---|---|
| event_id | TEXT | Yes | Yes |
| po_id | TEXT | No | Yes |
| previous_status | TEXT | No | No |
| new_status | TEXT | No | Yes |
| event_timestamp | TEXT | No | Yes |
| event_type | TEXT | No | Yes |

### Foreign Keys

- `po_id` references `purchase_order.po_id`

## shortage

| Column | Type | Primary Key | Required |
|---|---|---|---|
| shortage_id | TEXT | Yes | Yes |
| sku_id | TEXT | No | Yes |
| location_id | TEXT | No | Yes |
| week | TEXT | No | Yes |
| forecast_qty | INTEGER | No | Yes |
| inbound_qty | INTEGER | No | Yes |
| opening_balance | INTEGER | No | Yes |
| projected_balance | INTEGER | No | Yes |
| backlog_qty | INTEGER | No | Yes |
| new_shortage_qty | INTEGER | No | Yes |
| shortage_ratio | REAL | No | Yes |
| severity | TEXT | No | Yes |
| cause | TEXT | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- `location_id` references `location.location_id`
- `sku_id` references `sku.sku_id`

## sku

| Column | Type | Primary Key | Required |
|---|---|---|---|
| sku_id | TEXT | Yes | Yes |
| sku_name | TEXT | No | Yes |
| category | TEXT | No | Yes |
| unit_of_measure | TEXT | No | Yes |
| unit_cost | REAL | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- None

## supplier

| Column | Type | Primary Key | Required |
|---|---|---|---|
| supplier_id | TEXT | Yes | Yes |
| supplier_name | TEXT | No | Yes |
| country | TEXT | No | Yes |
| supplier_type | TEXT | No | Yes |
| reliability_score | REAL | No | Yes |
| status | TEXT | No | Yes |

### Foreign Keys

- None

## supplier_capacity

| Column | Type | Primary Key | Required |
|---|---|---|---|
| capacity_id | TEXT | Yes | Yes |
| supplier_sku_id | TEXT | No | Yes |
| supplier_id | TEXT | No | Yes |
| sku_id | TEXT | No | Yes |
| week | TEXT | No | Yes |
| maximum_capacity | INTEGER | No | Yes |
| available_capacity | INTEGER | No | Yes |
| capacity_constrained | INTEGER | No | Yes |

### Foreign Keys

- `supplier_sku_id` references `supplier_sku.supplier_sku_id`

## supplier_sku

| Column | Type | Primary Key | Required |
|---|---|---|---|
| supplier_sku_id | TEXT | Yes | Yes |
| supplier_id | TEXT | No | Yes |
| sku_id | TEXT | No | Yes |
| minimum_order_qty | INTEGER | No | Yes |
| approval_status | TEXT | No | Yes |
| effective_from | TEXT | No | Yes |
| effective_to | TEXT | No | Yes |

### Foreign Keys

- `sku_id` references `sku.sku_id`
- `supplier_id` references `supplier.supplier_id`

