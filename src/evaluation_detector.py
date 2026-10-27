from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")
ANOMALY_DIR = DATA_DIR / "anomalies"


def detect_evaluation_cases():
    cases = pd.read_csv(
        ANOMALY_DIR / "evaluation_input.csv",
        dtype={"observed_value": str}
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

        issue = "NO_ISSUE"
        reference_id = case.reference_id
        observed = str(case.observed_value)

        if case.entity_type == "PURCHASE_ORDER_RECEIPT":

            if reference_id not in po_lookup.index:
                raise ValueError(
                    f"Unknown purchase order: {reference_id}"
                )

            ordered_qty = int(
                po_lookup.loc[reference_id, "quantity"]
            )

            received_qty = int(observed)

            if received_qty > ordered_qty:
                issue = "INBOUND_COUNTED_TWICE"

        elif case.entity_type == "SUPPLIER_CAPACITY":

            if reference_id not in capacity_lookup.index:
                raise ValueError(
                    f"Unknown capacity record: {reference_id}"
                )

            available = int(
                capacity_lookup.loc[
                    reference_id,
                    "available_capacity"
                ]
            )

            requested_qty = int(observed)

            if requested_qty > available:
                issue = "SUPPLIER_CAPACITY_EXCEEDED"

        elif case.entity_type == "INVENTORY":

            if reference_id not in sku_lookup.index:
                raise ValueError(
                    f"Unknown SKU: {reference_id}"
                )

            expected_uom = str(
                sku_lookup.loc[
                    reference_id,
                    "unit_of_measure"
                ]
            )

            if observed != expected_uom:
                issue = "UOM_MISMATCH"

        elif case.entity_type == "SKU_SUBSTITUTION":

            if observed != "APPROVED":
                issue = "SUBSTITUTE_NOT_APPROVED"

        else:
            raise ValueError(
                f"Unsupported entity type: {case.entity_type}"
            )

        results.append({
            "case_id": case.case_id,
            "detected_issue": issue,
            "predicted_anomaly": issue != "NO_ISSUE"
        })

    results_df = pd.DataFrame(results)

    output_path = (
        ANOMALY_DIR / "evaluation_predictions.csv"
    )

    results_df.to_csv(
        output_path,
        index=False
    )

    print("\n========== EVALUATION DETECTION ==========")
    print(f"Cases evaluated: {len(results_df)}")

    print(
        "Predicted anomalies:",
        int(results_df["predicted_anomaly"].sum())
    )

    print(
        "Predicted normal:",
        int((~results_df["predicted_anomaly"]).sum())
    )

    print(f"Saved to: {output_path}")

    return results_df


if __name__ == "__main__":
    detect_evaluation_cases()