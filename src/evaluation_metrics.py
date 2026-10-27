import json
from pathlib import Path

import pandas as pd


ANOMALY_DIR = Path("data/anomalies")
DOCS_DIR = Path("docs")


def evaluate_predictions():
    predictions = pd.read_csv(
        ANOMALY_DIR / "evaluation_predictions.csv"
    )

    truth = pd.read_csv(
        ANOMALY_DIR / "evaluation_ground_truth.csv"
    )

    if predictions["case_id"].duplicated().any():
        raise ValueError("Duplicate prediction IDs found.")

    if truth["case_id"].duplicated().any():
        raise ValueError("Duplicate ground-truth IDs found.")

    if set(predictions["case_id"]) != set(truth["case_id"]):
        raise ValueError(
            "Prediction and ground-truth case IDs do not match."
        )

    evaluation = truth.merge(
        predictions,
        on="case_id",
        validate="one_to_one"
    )

    actual = evaluation["issue_type"] != "NO_ISSUE"
    predicted = evaluation["detected_issue"] != "NO_ISSUE"

    tp = int((actual & predicted).sum())
    tn = int((~actual & ~predicted).sum())
    fp = int((~actual & predicted).sum())
    fn = int((actual & ~predicted).sum())

    total = len(evaluation)

    accuracy = (tp + tn) / total if total else 0

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0
    )

    false_positive_rate = (
        fp / (fp + tn)
        if fp + tn
        else 0
    )

    classification_accuracy = (
        evaluation["issue_type"]
        == evaluation["detected_issue"]
    ).mean()

    metrics = {
        "total_cases": total,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positive_rate": false_positive_rate,
        "issue_classification_accuracy": float(
            classification_accuracy
        )
    }

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = DOCS_DIR / "anomaly_metrics.json"

    output_path.write_text(
        json.dumps(metrics, indent=4),
        encoding="utf-8"
    )

    print("\n========== ANOMALY EVALUATION ==========")

    print(f"Total cases: {total}")
    print(f"True positives: {tp}")
    print(f"True negatives: {tn}")
    print(f"False positives: {fp}")
    print(f"False negatives: {fn}")

    print(f"\nAccuracy: {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"F1-score: {f1:.2%}")
    print(f"False-positive rate: {false_positive_rate:.2%}")

    print(
        "Issue classification accuracy:",
        f"{classification_accuracy:.2%}"
    )

    print(f"\nSaved to: {output_path}")

    return metrics


if __name__ == "__main__":
    evaluate_predictions()