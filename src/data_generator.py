import pandas as pd
import numpy as np
from pathlib import Path

# Fixed seed ensures reproducible data
SEED = 20261022
rng = np.random.default_rng(SEED)

# Directory to save datasets
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def generate_skus(num_skus=3000):
    """
    Generate synthetic SKU master data.
    """

    categories = [
        "Electronics",
        "Furniture",
        "Clothing",
        "Automotive",
        "Industrial"
    ]

    records = []

    for i in range(1, num_skus + 1):

        sku_id = f"SKU-{i:06d}"

        category = rng.choice(categories)

        unit_cost = round(float(rng.uniform(100, 10000)), 2)

        records.append({
            "sku_id": sku_id,
            "sku_name": f"{category} Product {i}",
            "category": category,
            "unit_of_measure": "EA",
            "unit_cost": unit_cost,
            "status": "ACTIVE"
        })

    df = pd.DataFrame(records)

    # Validate unique primary keys
    assert df["sku_id"].is_unique, "Duplicate SKU IDs found"

    # Save to CSV
    output_path = DATA_DIR / "sku.csv"
    df.to_csv(output_path, index=False)

    print(f"Successfully generated {len(df)} SKUs")
    print(f"Saved to: {output_path}")

    return df

def generate_locations(num_locations=50):
    """
    Generate synthetic warehouse and distribution locations.
    """

    cities = [
        "Hyderabad", "Mumbai", "Delhi", "Bengaluru",
        "Chennai", "Pune", "Kolkata", "Ahmedabad",
        "Jaipur", "Lucknow"
    ]

    location_types = [
        "WAREHOUSE",
        "DISTRIBUTION_CENTER",
        "PRODUCTION_FACILITY"
    ]

    records = []

    for i in range(1, num_locations + 1):

        location_id = f"LOC-{i:04d}"

        city = cities[(i - 1) % len(cities)]

        location_type = rng.choice(location_types)

        records.append({
            "location_id": location_id,
            "location_name": f"{city} Facility {i}",
            "city": city,
            "location_type": location_type,
            "status": "ACTIVE"
        })

    df = pd.DataFrame(records)

    assert df["location_id"].is_unique, "Duplicate Location IDs found"

    output_path = DATA_DIR / "location.csv"

    df.to_csv(output_path, index=False)

    print(f"Successfully generated {len(df)} locations")
    print(f"Saved to: {output_path}")

    return df

def generate_suppliers(num_suppliers=500):
    """
    Generate synthetic supplier master data.
    """

    countries = [
        "India",
        "United States",
        "Germany",
        "Japan",
        "China",
        "United Kingdom",
        "South Korea",
        "Singapore"
    ]

    supplier_types = [
        "MANUFACTURER",
        "DISTRIBUTOR",
        "WHOLESALER"
    ]

    records = []

    for i in range(1, num_suppliers + 1):

        supplier_id = f"SUP-{i:04d}"

        country = rng.choice(countries)
        supplier_type = rng.choice(supplier_types)

        reliability_score = round(
            float(rng.uniform(0.70, 0.99)), 3
        )

        records.append({
            "supplier_id": supplier_id,
            "supplier_name": f"Supplier Company {i}",
            "country": country,
            "supplier_type": supplier_type,
            "reliability_score": reliability_score,
            "status": "ACTIVE"
        })

    df = pd.DataFrame(records)

    # Validate unique supplier IDs
    assert df["supplier_id"].is_unique, "Duplicate Supplier IDs found"

    output_path = DATA_DIR / "supplier.csv"

    df.to_csv(output_path, index=False)

    print(f"Successfully generated {len(df)} suppliers")
    print(f"Saved to: {output_path}")

    return df

def generate_forecast_demand(skus, locations, num_weeks=52):
    """
    Generate weekly forecast demand for SKU-location combinations.
    Uses a fixed seed for reproducibility.
    """

    demand_rng = np.random.default_rng(SEED + 100)

    records = []

    # Each SKU is assigned to 3 valid locations.
    # This keeps the dataset reasonably sized.
    for sku_id in skus["sku_id"]:

        assigned_locations = demand_rng.choice(
            locations["location_id"].to_numpy(),
            size=min(3, len(locations)),
            replace=False
        )

        base_demand = int(demand_rng.integers(40, 250))

        for location_id in assigned_locations:

            location_factor = float(
                demand_rng.uniform(0.7, 1.3)
            )

            for week in range(1, num_weeks + 1):

                # Seasonal variation
                seasonal_factor = (
                    1.0 if week <= 13
                    else 1.15 if week <= 26
                    else 0.9 if week <= 39
                    else 1.35
                )

                # Small random demand variation
                variation = float(
                    demand_rng.uniform(0.85, 1.15)
                )

                # Introduce occasional demand spikes
                is_spike = demand_rng.random() < 0.03

                spike_factor = (
                    float(demand_rng.uniform(1.5, 2.5))
                    if is_spike else 1.0
                )

                forecast_qty = max(
                    0,
                    round(
                        base_demand
                        * location_factor
                        * seasonal_factor
                        * variation
                        * spike_factor
                    )
                )

                demand_id = (
                    f"DEM-{sku_id}-{location_id}-2026W{week:02d}"
                )

                records.append({
                    "demand_id": demand_id,
                    "sku_id": sku_id,
                    "location_id": location_id,
                    "week": f"2026W{week:02d}",
                    "forecast_qty": forecast_qty,
                    "demand_spike": bool(is_spike),
                    "status": "ACTIVE"
                })

    df = pd.DataFrame(records)

    # Primary-key validation
    assert df["demand_id"].is_unique, (
        "Duplicate demand IDs found"
    )

    # Foreign-key validation
    assert df["sku_id"].isin(skus["sku_id"]).all(), (
        "Invalid SKU references found"
    )

    assert df["location_id"].isin(
        locations["location_id"]
    ).all(), "Invalid location references found"

    # Validate forecast quantities
    assert (df["forecast_qty"] >= 0).all(), (
        "Negative demand detected"
    )

    output_path = DATA_DIR / "forecast_demand.csv"

    df.to_csv(output_path, index=False)

    print(f"Successfully generated {len(df):,} demand records")
    print(f"Saved to: {output_path}")

    return df
def generate_inventory(forecast_demand):
    """
    Generate starting inventory for every SKU-location pair
    present in the demand forecast.
    """

    inventory_rng = np.random.default_rng(SEED + 200)

    # Extract unique SKU-location combinations
    sku_locations = (
        forecast_demand[["sku_id", "location_id"]]
        .drop_duplicates()
        .sort_values(["sku_id", "location_id"])
        .reset_index(drop=True)
    )

    records = []

    for i, row in enumerate(
        sku_locations.itertuples(index=False), start=1
    ):
        sku_id = row.sku_id
        location_id = row.location_id

        # Synthetic starting inventory
        on_hand_qty = int(
            inventory_rng.integers(100, 1501)
        )

        # Reserve some stock for existing commitments
        reserved_qty = int(
            on_hand_qty * inventory_rng.uniform(0.0, 0.15)
        )

        available_qty = on_hand_qty - reserved_qty

        records.append({
            "inventory_id": f"INV-{i:06d}",
            "sku_id": sku_id,
            "location_id": location_id,
            "snapshot_date": "2025-12-29",
            "on_hand_qty": on_hand_qty,
            "reserved_qty": reserved_qty,
            "available_qty": available_qty,
            "unit_of_measure": "EA",
            "status": "ACTIVE"
        })

    df = pd.DataFrame(records)

    # Validate unique inventory IDs
    assert df["inventory_id"].is_unique, (
        "Duplicate inventory IDs found"
    )

    # Verify inventory calculations
    assert (
        df["available_qty"]
        == df["on_hand_qty"] - df["reserved_qty"]
    ).all(), "Inventory balance calculation failed"

    # Verify non-negative quantities
    assert (df["available_qty"] >= 0).all(), (
        "Negative inventory detected"
    )

    output_path = DATA_DIR / "inventory.csv"

    df.to_csv(output_path, index=False)

    print(
        f"Successfully generated {len(df):,} inventory records"
    )
    print(f"Saved to: {output_path}")

    return df

def generate_supplier_capacities(skus, suppliers, num_weeks=52):
    """
    Generate approved supplier-SKU relationships
    and weekly supplier capacity records.
    """

    capacity_rng = np.random.default_rng(SEED + 300)

    supplier_ids = suppliers["supplier_id"].to_numpy()

    relationships = []
    capacity_records = []
    lead_time_records = []

    relationship_counter = 1
    capacity_counter = 1

    for sku_id in skus["sku_id"]:

        # Assign two approved suppliers to each SKU.
        assigned_suppliers = capacity_rng.choice(
            supplier_ids,
            size=2,
            replace=False
        )

        for supplier_id in assigned_suppliers:

            relationship_id = f"SS-{relationship_counter:06d}"

            weekly_capacity = int(
                capacity_rng.integers(200, 1201)
            )

            minimum_order_qty = int(
                capacity_rng.choice([10, 25, 50, 100])
            )

            lead_time_days = int(
                capacity_rng.integers(3, 29)
            )

            relationships.append({
                "supplier_sku_id": relationship_id,
                "supplier_id": supplier_id,
                "sku_id": sku_id,
                "minimum_order_qty": minimum_order_qty,
                "approval_status": "APPROVED",
                "effective_from": "2025-12-01",
                "effective_to": "2026-12-31"
            })

            lead_time_records.append({
                "lead_time_id": f"LT-{relationship_counter:06d}",
                "supplier_sku_id": relationship_id,
                "supplier_id": supplier_id,
                "sku_id": sku_id,
                "lead_time_days": lead_time_days,
                "effective_from": "2025-12-01",
                "effective_to": "2026-12-31"
            })

            for week in range(1, num_weeks + 1):

                # Some suppliers experience reduced capacity.
                constrained = (
                    capacity_rng.random() < 0.08
                )

                capacity_factor = 0.5 if constrained else 1.0

                available_capacity = int(
                    weekly_capacity * capacity_factor
                )

                capacity_records.append({
                    "capacity_id": f"CAP-{capacity_counter:08d}",
                    "supplier_sku_id": relationship_id,
                    "supplier_id": supplier_id,
                    "sku_id": sku_id,
                    "week": f"2026W{week:02d}",
                    "maximum_capacity": weekly_capacity,
                    "available_capacity": available_capacity,
                    "capacity_constrained": constrained
                })

                capacity_counter += 1

            relationship_counter += 1

    relationships_df = pd.DataFrame(relationships)
    capacity_df = pd.DataFrame(capacity_records)
    lead_time_df = pd.DataFrame(lead_time_records)

    # Primary key validations
    assert relationships_df["supplier_sku_id"].is_unique
    assert capacity_df["capacity_id"].is_unique
    assert lead_time_df["lead_time_id"].is_unique

    # Foreign key validations
    assert relationships_df["sku_id"].isin(
        skus["sku_id"]
    ).all()

    assert relationships_df["supplier_id"].isin(
        suppliers["supplier_id"]
    ).all()

    assert capacity_df["supplier_sku_id"].isin(
        relationships_df["supplier_sku_id"]
    ).all()

    assert lead_time_df["supplier_sku_id"].isin(
        relationships_df["supplier_sku_id"]
    ).all()

    # Capacity cannot exceed the maximum.
    assert (
        capacity_df["available_capacity"]
        <= capacity_df["maximum_capacity"]
    ).all()

    assert (
        capacity_df["available_capacity"] >= 0
    ).all()

    # Lead times must be positive.
    assert (
        lead_time_df["lead_time_days"] > 0
    ).all()

    # Export datasets
    relationships_df.to_csv(
        DATA_DIR / "supplier_sku.csv",
        index=False
    )

    capacity_df.to_csv(
        DATA_DIR / "supplier_capacity.csv",
        index=False
    )

    lead_time_df.to_csv(
        DATA_DIR / "lead_time.csv",
        index=False
    )

    print(
        f"Generated {len(relationships_df):,} supplier-SKU relationships"
    )

    print(
        f"Generated {len(capacity_df):,} supplier capacity records"
    )

    print(
        f"Generated {len(lead_time_df):,} lead time records"
    )

    return relationships_df, capacity_df, lead_time_df

def generate_purchase_orders(
    supplier_sku,
    supplier_capacity,
    lead_time,
    forecast_demand,
    num_orders=10000
):
    """
    Generate synthetic inbound purchase orders using valid
    supplier-SKU relationships, lead times, and capacity.

    Orders are scheduled before their expected receipt weeks.
    """

    po_rng = np.random.default_rng(SEED + 400)

    # Valid demand-based destinations
    valid_pairs = (
        forecast_demand[["sku_id", "location_id"]]
        .drop_duplicates()
    )

    # Supplier-SKU master data
    supply = supplier_sku.merge(
        lead_time[["supplier_sku_id", "lead_time_days"]],
        on="supplier_sku_id",
        validate="one_to_one"
    )

    supply = supply.merge(
        valid_pairs,
        on="sku_id",
        validate="many_to_many"
    )

    # Capacity lookup
    capacity_lookup = {
        (row.supplier_sku_id, row.week): int(row.available_capacity)
        for row in supplier_capacity.itertuples(index=False)
    }

    # Track capacity committed to existing POs
    committed = {}

    records = []

    start_date = pd.Timestamp("2025-12-29")
    order_counter = 1

    # Attempt more candidates than required because some
    # candidates may fail capacity or quantity checks.
    max_attempts = num_orders * 30
    attempts = 0

    while len(records) < num_orders and attempts < max_attempts:
        attempts += 1

        row = supply.iloc[
            int(po_rng.integers(0, len(supply)))
        ]

        relationship_id = row["supplier_sku_id"]
        sku_id = row["sku_id"]
        supplier_id = row["supplier_id"]
        location_id = row["location_id"]

        lead_days = int(row["lead_time_days"])
        minimum_qty = int(row["minimum_order_qty"])

        # Choose an order date during the planning horizon.
        day_offset = int(po_rng.integers(0, 330))
        order_date = start_date + pd.Timedelta(days=day_offset)

        expected_delivery = order_date + pd.Timedelta(
            days=lead_days
        )

        # Introduce realistic transport delays.
        is_delayed = bool(po_rng.random() < 0.12)

        delay_days = (
            int(po_rng.integers(2, 15))
            if is_delayed else 0
        )

        revised_delivery = expected_delivery + pd.Timedelta(
            days=delay_days
        )

        # ISO week for supplier capacity allocation
        capacity_week = (
            order_date.isocalendar()
        )

        week_label = (
            f"{capacity_week.year}W{capacity_week.week:02d}"
        )

        capacity_key = (relationship_id, week_label)

        maximum_available = capacity_lookup.get(
            capacity_key, 0
        )

        already_committed = committed.get(
            capacity_key, 0
        )

        remaining_capacity = (
            maximum_available - already_committed
        )

        if remaining_capacity < minimum_qty:
            continue

        # Order quantity respects MOQ and remaining capacity.
        upper_qty = min(remaining_capacity, 800)

        if upper_qty < minimum_qty:
            continue

        quantity = int(
            po_rng.integers(minimum_qty, upper_qty + 1)
        )

        # Reserve capacity for the order.
        committed[capacity_key] = (
            already_committed + quantity
        )

        # Simulate purchase order lifecycle.
        # Status is based on the synthetic delivery event.
        if is_delayed:
            status = "DELAYED"
        else:
            status = "CONFIRMED"

        records.append({
            "po_id": f"PO-2026-{order_counter:06d}",
            "supplier_sku_id": relationship_id,
            "supplier_id": supplier_id,
            "sku_id": sku_id,
            "location_id": location_id,
            "order_date": order_date.date().isoformat(),
            "expected_delivery_date": (
                expected_delivery.date().isoformat()
            ),
            "revised_delivery_date": (
                revised_delivery.date().isoformat()
            ),
            "quantity": quantity,
            "unit_of_measure": "EA",
            "status": status,
            "transport_delayed": is_delayed,
            "delay_days": delay_days
        })

        order_counter += 1

    df = pd.DataFrame(records)

    if len(df) != num_orders:
        raise RuntimeError(
            f"Generated {len(df)} purchase orders instead "
            f"of {num_orders}. Increase candidate attempts "
            f"or review supplier capacity."
        )

    # Validate primary keys
    assert df["po_id"].is_unique, (
        "Duplicate purchase order IDs found"
    )

    # Validate supplier-SKU foreign keys
    assert df["supplier_sku_id"].isin(
        supplier_sku["supplier_sku_id"]
    ).all()

    # Check date ordering
    assert (
        pd.to_datetime(df["expected_delivery_date"])
        >= pd.to_datetime(df["order_date"])
    ).all()

    assert (
        pd.to_datetime(df["revised_delivery_date"])
        >= pd.to_datetime(df["expected_delivery_date"])
    ).all()

    # Check quantities
    assert (df["quantity"] > 0).all()

    output_path = DATA_DIR / "purchase_order.csv"

    df.to_csv(output_path, index=False)

    print(
        f"Successfully generated {len(df):,} purchase orders"
    )
    print(f"Transport delays: {df['transport_delayed'].sum():,}")
    print(f"Saved to: {output_path}")

    return df


if __name__ == "__main__":

    skus = generate_skus()
    locations = generate_locations()
    suppliers = generate_suppliers()

    forecast_demand = generate_forecast_demand(
        skus,
        locations,
        num_weeks=52
    )

    inventory = generate_inventory(forecast_demand)

    supplier_sku, supplier_capacity, lead_time = (
        generate_supplier_capacities(
            skus,
            suppliers,
            num_weeks=52
        )
    )

    purchase_orders = generate_purchase_orders(
        supplier_sku,
        supplier_capacity,
        lead_time,
        forecast_demand,
        num_orders=10000
    )