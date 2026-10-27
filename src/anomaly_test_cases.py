from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
ANOMALY_DIR = DATA_DIR / "anomalies"


def generate_test_cases():
    ANOMALY_DIR.mkdir(parents=True, exist_ok=True)

    purchase_orders = pd.read_csv(
        DATA_DIR / "purchase_order.csv"
    )

    supplier_capacity = pd.read_csv(
        DATA_DIR / "supplier_capacity.csv"
    )

    skus = pd.read_csv(
        DATA_DIR / "sku.csv"
    )

    po = purchase_orders.iloc[0]
    capacity = supplier_capacity.iloc[0]
    sku = skus.iloc[0]

    cases = [
        {
            "case_id": "TEST-000001",
            "entity_type": "PURCHASE_ORDER_RECEIPT",
            "reference_id": po["po_id"],
            "observed_value": str(int(po["quantity"])),
            "expected_value": str(int(po["quantity"])),
            "issue_type": "NO_ISSUE"
        },
        {
            "case_id": "TEST-000002",
            "entity_type": "PURCHASE_ORDER_RECEIPT",
            "reference_id": po["po_id"],
            "observed_value": str(int(po["quantity"]) * 2),
            "expected_value": str(int(po["quantity"])),
            "issue_type": "INBOUND_COUNTED_TWICE"
        },
        {
            "case_id": "TEST-000003",
            "entity_type": "SUPPLIER_CAPACITY",
            "reference_id": capacity["capacity_id"],
            "observed_value": str(int(capacity["available_capacity"])),
            "expected_value": str(int(capacity["available_capacity"])),
            "issue_type": "NO_ISSUE"
        },
        {
            "case_id": "TEST-000004",
            "entity_type": "SUPPLIER_CAPACITY",
            "reference_id": capacity["capacity_id"],
            "observed_value": str(int(capacity["available_capacity"]) + 100),
            "expected_value": str(int(capacity["available_capacity"])),
            "issue_type": "SUPPLIER_CAPACITY_EXCEEDED"
        },
        {
            "case_id": "TEST-000005",
            "entity_type": "INVENTORY",
            "reference_id": sku["sku_id"],
            "observed_value": sku["unit_of_measure"],
            "expected_value": sku["unit_of_measure"],
            "issue_type": "NO_ISSUE"
        },
        {
            "case_id": "TEST-000006",
            "entity_type": "INVENTORY",
            "reference_id": sku["sku_id"],
            "observed_value": "BOX",
            "expected_value": sku["unit_of_measure"],
            "issue_type": "UOM_MISMATCH"
        },
        {
            "case_id": "TEST-000007",
            "entity_type": "SKU_SUBSTITUTION",
            "reference_id": sku["sku_id"],
            "observed_value": "APPROVED",
            "expected_value": "APPROVED",
            "issue_type": "NO_ISSUE"
        },
        {
            "case_id": "TEST-000008",
            "entity_type": "SKU_SUBSTITUTION",
            "reference_id": sku["sku_id"],
            "observed_value": "UNAPPROVED",
            "expected_value": "APPROVED",
            "issue_type": "SUBSTITUTE_NOT_APPROVED"
        }
    ]

    input_records = pd.DataFrame(cases)

    ground_truth = input_records[
        ["case_id", "issue_type"]
    ].copy()

    detector_input = input_records[
        [
            "case_id",
            "entity_type",
            "reference_id",
            "observed_value"
        ]
    ].copy()

    detector_input.to_csv(
        ANOMALY_DIR / "evaluation_input.csv",
        index=False
    )

    ground_truth.to_csv(
        ANOMALY_DIR / "evaluation_ground_truth.csv",
        index=False
    )

    print("\n========== EVALUATION DATA ==========")
    print(f"Total cases: {len(input_records)}")
    print(f"Normal cases: {(ground_truth['issue_type'] == 'NO_ISSUE').sum()}")
    print(f"Anomaly cases: {(ground_truth['issue_type'] != 'NO_ISSUE').sum()}")


if __name__ == "__main__":
    generate_test_cases()