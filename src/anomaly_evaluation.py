from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
ANOMALY_DIR = DATA_DIR / "anomalies"


def evaluate_detection():

    predictions = pd.read_csv(
        ANOMALY_DIR / "detection_results.csv"
    )

    ground_truth = pd.read_csv(
        DATA_DIR / "ground_truth.csv"
    )

    evaluation = ground_truth.merge(
        predictions,
        on="case_id",
        how="left",
        validate="one_to_one"
    )

    if evaluation["detected_issue"].isna().any():
        raise ValueError("Some cases have no predictions.")

    evaluation["correct_issue"] = (
        evaluation["issue_type"]
        == evaluation["detected_issue"]
    )

    evaluation["correct_decision"] = (
        evaluation["expected_decision"]
        == evaluation["decision"]
    )

    accuracy = evaluation["correct_issue"].mean()
    decision_accuracy = evaluation["correct_decision"].mean()

    print("\n========== ANOMALY EVALUATION ==========")

    print(f"Total evaluated cases: {len(evaluation)}")
    print(f"Issue classification accuracy: {accuracy:.2%}")
    print(f"Decision accuracy: {decision_accuracy:.2%}")

    evaluation.to_csv(
        ANOMALY_DIR / "evaluation_results.csv",
        index=False
    )

    return evaluation


if __name__ == "__main__":
    evaluate_detection()