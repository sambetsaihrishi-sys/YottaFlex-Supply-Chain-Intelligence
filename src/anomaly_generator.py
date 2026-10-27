import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
ANOMALY_DIR = DATA_DIR / "anomalies"


def generate_anomalies():
    ANOMALY_DIR.mkdir(parents=True, exist_ok=True)

    purchase_orders = pd.read_csv(
        DATA_DIR / "purchase_order.csv"
    )

    supplier_capacity = pd.read_csv(
        DATA_DIR / "supplier_capacity.csv"
    )

    supplier_sku = pd.read_csv(
        DATA_DIR / "supplier_sku.csv"
    )

    shortages = pd.read_csv(
        DATA_DIR / "shortage.csv"
    )

    skus = pd.read_csv(
        DATA_DIR / "sku.csv"
    )

    anomalies = []
    ground_truth = []

    def add_case(case_id, issue_type, record, expected_decision):
        anomalies.append({
            "case_id": case_id,
            "entity_type": record["entity_type"],
            "reference_id": record["reference_id"],
            "issue_type_hidden": "",
            "observed_value": record["observed_value"],
            "expected_value": record["expected_value"]
        })

        ground_truth.append({
            "case_id": case_id,
            "issue_type": issue_type,
            "reference_id": record["reference_id"],
            "expected_decision": expected_decision
        })

    po = purchase_orders.iloc[0]

    add_case(
        "ANOM-000001",
        "INBOUND_COUNTED_TWICE",
        {
            "entity_type": "PURCHASE_ORDER_RECEIPT",
            "reference_id": po["po_id"],
            "observed_value": int(po["quantity"]) * 2,
            "expected_value": int(po["quantity"])
        },
        "REJECT_DUPLICATE_INBOUND"
    )

    capacity = supplier_capacity.iloc[0]

    add_case(
        "ANOM-000002",
        "SUPPLIER_CAPACITY_EXCEEDED",
        {
            "entity_type": "SUPPLIER_CAPACITY",
            "reference_id": capacity["capacity_id"],
            "observed_value": int(
                capacity["available_capacity"]
            ) + 100,
            "expected_value": int(
                capacity["available_capacity"]
            )
        },
        "REJECT_CAPACITY_VIOLATION"
    )

    shortage = shortages.iloc[0]

    add_case(
        "ANOM-000003",
        "LEAD_TIME_IGNORED",
        {
            "entity_type": "SHORTAGE_MITIGATION",
            "reference_id": shortage["shortage_id"],
            "observed_value": "IMMEDIATE_DELIVERY",
            "expected_value": "CHECK_SUPPLIER_LEAD_TIME"
        },
        "RECALCULATE_DELIVERY_FEASIBILITY"
    )

    sku = skus.iloc[0]

    add_case(
        "ANOM-000004",
        "UOM_MISMATCH",
        {
            "entity_type": "INVENTORY",
            "reference_id": sku["sku_id"],
            "observed_value": "BOX",
            "expected_value": sku["unit_of_measure"]
        },
        "REJECT_INCOMPATIBLE_UNIT"
    )

    relation = supplier_sku.iloc[0]

    add_case(
        "ANOM-000005",
        "SUBSTITUTE_NOT_APPROVED",
        {
            "entity_type": "SKU_SUBSTITUTION",
            "reference_id": relation["sku_id"],
            "observed_value": "UNAPPROVED",
            "expected_value": "APPROVED"
        },
        "REJECT_UNAPPROVED_SUBSTITUTE"
    )

    anomaly_df = pd.DataFrame(anomalies)
    truth_df = pd.DataFrame(ground_truth)

    anomaly_df.to_csv(
        ANOMALY_DIR / "anomaly_cases.csv",
        index=False
    )

    truth_df.to_csv(
        DATA_DIR / "ground_truth.csv",
        index=False
    )

    print("\n========== ANOMALY GENERATION ==========")
    print(f"Anomaly cases: {len(anomaly_df)}")
    print(f"Ground truth labels: {len(truth_df)}")
    print("Generated all five required anomaly types.")

    return anomaly_df, truth_df


if __name__ == "__main__":
    generate_anomalies()