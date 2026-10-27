from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
ANOMALY_DIR = DATA_DIR / "anomalies"


def detect_anomalies():

    print("\nLoading anomaly detection inputs...")

    cases = pd.read_csv(
        ANOMALY_DIR / "anomaly_cases.csv"
    )

    purchase_orders = pd.read_csv(
        DATA_DIR / "purchase_order.csv"
    )

    supplier_capacity = pd.read_csv(
        DATA_DIR / "supplier_capacity.csv"
    )

    skus = pd.read_csv(
        DATA_DIR / "sku.csv"
    )

    po_lookup = purchase_orders.set_index("po_id")
    capacity_lookup = supplier_capacity.set_index("capacity_id")
    sku_lookup = skus.set_index("sku_id")

    results = []

    for case in cases.itertuples(index=False):

        detected_issue = "NO_ISSUE"
        decision = "ACCEPT"

        reference_id = case.reference_id
        observed_value = str(case.observed_value)
        entity_type = case.entity_type

        if entity_type == "PURCHASE_ORDER_RECEIPT":

            if reference_id in po_lookup.index:

                expected_qty = int(
                    po_lookup.loc[reference_id, "quantity"]
                )

                if int(observed_value) > expected_qty:
                    detected_issue = "INBOUND_COUNTED_TWICE"
                    decision = "REJECT_DUPLICATE_INBOUND"

        elif entity_type == "SUPPLIER_CAPACITY":

            if reference_id in capacity_lookup.index:

                available = int(
                    capacity_lookup.loc[
                        reference_id, "available_capacity"
                    ]
                )

                if int(observed_value) > available:
                    detected_issue = "SUPPLIER_CAPACITY_EXCEEDED"
                    decision = "REJECT_CAPACITY_VIOLATION"

        elif entity_type == "SHORTAGE_MITIGATION":

            if observed_value == "IMMEDIATE_DELIVERY":
                detected_issue = "LEAD_TIME_IGNORED"
                decision = "RECALCULATE_DELIVERY_FEASIBILITY"

        elif entity_type == "INVENTORY":

            if reference_id in sku_lookup.index:

                expected_uom = str(
                    sku_lookup.loc[
                        reference_id, "unit_of_measure"
                    ]
                )

                if observed_value != expected_uom:
                    detected_issue = "UOM_MISMATCH"
                    decision = "REJECT_INCOMPATIBLE_UNIT"

        elif entity_type == "SKU_SUBSTITUTION":

            if observed_value == "UNAPPROVED":
                detected_issue = "SUBSTITUTE_NOT_APPROVED"
                decision = "REJECT_UNAPPROVED_SUBSTITUTE"

        results.append({
            "case_id": case.case_id,
            "reference_id": reference_id,
            "detected_issue": detected_issue,
            "decision": decision
        })

    results_df = pd.DataFrame(results)

    results_df.to_csv(
        ANOMALY_DIR / "detection_results.csv",
        index=False
    )

    print("\n========== DETECTION RESULTS ==========")

    print(f"Total cases checked: {len(results_df)}")

    print(
        "Detected anomalies:",
        int((results_df["detected_issue"] != "NO_ISSUE").sum())
    )

    print("\nDetected issue types:")

    print(results_df["detected_issue"].value_counts())

    return results_df


if __name__ == "__main__":
    detect_anomalies()