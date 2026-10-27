# Supply Chain Data Dictionary

## Overview

This document describes the database tables and their fields.

Data is synthetically generated using seed 20261022.

## bom

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| bom_id | TEXT | Yes | Yes | - | - |
| parent_sku_id | TEXT | Yes | No | sku.sku_id | - |
| component_sku_id | TEXT | Yes | No | sku.sku_id | - |
| quantity_per_unit | INTEGER | Yes | No | - | - |
| effective_from | TEXT | Yes | No | - | - |
| effective_to | TEXT | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## forecast_demand

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| demand_id | TEXT | Yes | Yes | - | - |
| sku_id | TEXT | Yes | No | sku.sku_id | - |
| location_id | TEXT | Yes | No | location.location_id | - |
| week | TEXT | Yes | No | - | - |
| forecast_qty | INTEGER | Yes | No | - | - |
| demand_spike | INTEGER | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## inventory

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| inventory_id | TEXT | Yes | Yes | - | - |
| sku_id | TEXT | Yes | No | sku.sku_id | - |
| location_id | TEXT | Yes | No | location.location_id | - |
| snapshot_date | TEXT | Yes | No | - | - |
| on_hand_qty | INTEGER | Yes | No | - | - |
| reserved_qty | INTEGER | Yes | No | - | - |
| available_qty | INTEGER | Yes | No | - | - |
| unit_of_measure | TEXT | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## lead_time

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| lead_time_id | TEXT | Yes | Yes | - | - |
| supplier_sku_id | TEXT | Yes | No | supplier_sku.supplier_sku_id | - |
| supplier_id | TEXT | Yes | No | - | - |
| sku_id | TEXT | Yes | No | - | - |
| lead_time_days | INTEGER | Yes | No | - | - |
| effective_from | TEXT | Yes | No | - | - |
| effective_to | TEXT | Yes | No | - | - |

## location

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| location_id | TEXT | Yes | Yes | - | - |
| location_name | TEXT | Yes | No | - | - |
| city | TEXT | Yes | No | - | - |
| location_type | TEXT | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## mitigation_option

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| mitigation_id | TEXT | Yes | Yes | - | - |
| shortage_id | TEXT | Yes | No | shortage.shortage_id | - |
| sku_id | TEXT | Yes | No | sku.sku_id | - |
| location_id | TEXT | Yes | No | location.location_id | - |
| supplier_id | TEXT | Yes | No | supplier.supplier_id | - |
| supplier_sku_id | TEXT | Yes | No | supplier_sku.supplier_sku_id | - |
| required_qty | INTEGER | Yes | No | - | - |
| proposed_qty | INTEGER | Yes | No | - | - |
| minimum_order_qty | INTEGER | Yes | No | - | - |
| remaining_capacity | INTEGER | Yes | No | - | - |
| lead_time_days | INTEGER | Yes | No | - | - |
| order_date | TEXT | Yes | No | - | - |
| arrival_date | TEXT | Yes | No | - | - |
| estimated_unit_cost | REAL | Yes | No | - | - |
| estimated_total_cost | REAL | Yes | No | - | - |
| coverage_ratio | REAL | Yes | No | - | - |
| on_time | INTEGER | Yes | No | - | - |
| feasible | INTEGER | Yes | No | - | - |
| recommendation_status | TEXT | Yes | No | - | - |

## production_capacity

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| production_capacity_id | TEXT | Yes | Yes | - | - |
| sku_id | TEXT | Yes | No | sku.sku_id | - |
| location_id | TEXT | Yes | No | location.location_id | - |
| week | TEXT | Yes | No | - | - |
| maximum_capacity | INTEGER | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## production_plan

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| production_plan_id | TEXT | Yes | Yes | - | - |
| sku_id | TEXT | Yes | No | sku.sku_id | - |
| location_id | TEXT | Yes | No | location.location_id | - |
| week | TEXT | Yes | No | - | - |
| planned_qty | INTEGER | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## purchase_order

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| po_id | TEXT | Yes | Yes | - | - |
| supplier_sku_id | TEXT | Yes | No | supplier_sku.supplier_sku_id | - |
| supplier_id | TEXT | Yes | No | - | - |
| sku_id | TEXT | Yes | No | - | - |
| location_id | TEXT | Yes | No | location.location_id | - |
| order_date | TEXT | Yes | No | - | - |
| expected_delivery_date | TEXT | Yes | No | - | - |
| revised_delivery_date | TEXT | Yes | No | - | - |
| quantity | INTEGER | Yes | No | - | - |
| unit_of_measure | TEXT | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |
| transport_delayed | INTEGER | Yes | No | - | - |
| delay_days | INTEGER | Yes | No | - | - |

## purchase_order_event

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| event_id | TEXT | Yes | Yes | - | - |
| po_id | TEXT | Yes | No | purchase_order.po_id | - |
| previous_status | TEXT | No | No | - | - |
| new_status | TEXT | Yes | No | - | - |
| event_timestamp | TEXT | Yes | No | - | - |
| event_type | TEXT | Yes | No | - | - |

## shortage

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| shortage_id | TEXT | Yes | Yes | - | - |
| sku_id | TEXT | Yes | No | sku.sku_id | - |
| location_id | TEXT | Yes | No | location.location_id | - |
| week | TEXT | Yes | No | - | - |
| forecast_qty | INTEGER | Yes | No | - | - |
| inbound_qty | INTEGER | Yes | No | - | - |
| opening_balance | INTEGER | Yes | No | - | - |
| projected_balance | INTEGER | Yes | No | - | - |
| backlog_qty | INTEGER | Yes | No | - | - |
| new_shortage_qty | INTEGER | Yes | No | - | - |
| shortage_ratio | REAL | Yes | No | - | - |
| severity | TEXT | Yes | No | - | - |
| cause | TEXT | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## sku

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| sku_id | TEXT | Yes | Yes | - | - |
| sku_name | TEXT | Yes | No | - | - |
| category | TEXT | Yes | No | - | - |
| unit_of_measure | TEXT | Yes | No | - | - |
| unit_cost | REAL | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## supplier

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| supplier_id | TEXT | Yes | Yes | - | - |
| supplier_name | TEXT | Yes | No | - | - |
| country | TEXT | Yes | No | - | - |
| supplier_type | TEXT | Yes | No | - | - |
| reliability_score | REAL | Yes | No | - | - |
| status | TEXT | Yes | No | - | - |

## supplier_capacity

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| capacity_id | TEXT | Yes | Yes | - | - |
| supplier_sku_id | TEXT | Yes | No | supplier_sku.supplier_sku_id | - |
| supplier_id | TEXT | Yes | No | - | - |
| sku_id | TEXT | Yes | No | - | - |
| week | TEXT | Yes | No | - | - |
| maximum_capacity | INTEGER | Yes | No | - | - |
| available_capacity | INTEGER | Yes | No | - | - |
| capacity_constrained | INTEGER | Yes | No | - | - |

## supplier_sku

| Field | Data Type | Required | Primary Key | Foreign Key | Default |
|---|---|---|---|---|---|
| supplier_sku_id | TEXT | Yes | Yes | - | - |
| supplier_id | TEXT | Yes | No | supplier.supplier_id | - |
| sku_id | TEXT | Yes | No | sku.sku_id | - |
| minimum_order_qty | INTEGER | Yes | No | - | - |
| approval_status | TEXT | Yes | No | - | - |
| effective_from | TEXT | Yes | No | - | - |
| effective_to | TEXT | Yes | No | - | - |
