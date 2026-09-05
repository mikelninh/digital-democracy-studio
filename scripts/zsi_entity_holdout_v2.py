from __future__ import annotations

import json
from pathlib import Path

from zsi_entity_resolver_v12 import predict

ROOT = Path(__file__).resolve().parents[1]
HOLDOUT = ROOT / "zero-suffering-intelligence" / "entity-resolution" / "holdout-v2.json"
OUT = ROOT / "zero-suffering-intelligence" / "entity-resolution" / "results-holdout-v2.json"


def main() -> None:
    data = json.loads(HOLDOUT.read_text(encoding="utf-8"))

    rows = []
    true_positive_auto_merges = 0
    false_positive_auto_merges = 0
    true_negative_auto_separations = 0
    false_negative_auto_separations = 0
    review_on_true_merge = 0
    review_on_true_separate = 0

    for case in data["cases"]:
        predicted, reason, evidence = predict(case["record_a"], case["record_b"])
        expected = case["ground_truth"]

        if predicted == "merge":
            if expected == "merge":
                true_positive_auto_merges += 1
            else:
                false_positive_auto_merges += 1
        elif predicted == "separate":
            if expected == "separate":
                true_negative_auto_separations += 1
            else:
                false_negative_auto_separations += 1
        else:
            if expected == "merge":
                review_on_true_merge += 1
            else:
                review_on_true_separate += 1

        rows.append(
            {
                "case_id": case["case_id"],
                "expected": expected,
                "predicted": predicted,
                "correct_auto_decision": predicted != "review" and predicted == expected,
                "reason": reason,
                "record_a": case["record_a"]["name"],
                "record_b": case["record_b"]["name"],
                "ground_truth_reason": case["ground_truth_reason"],
                "evidence": evidence,
            }
        )

    total = len(rows)
    reviews = review_on_true_merge + review_on_true_separate
    covered = total - reviews

    precision_denominator = true_positive_auto_merges + false_positive_auto_merges
    auto_merge_precision = (
        true_positive_auto_merges / precision_denominator
        if precision_denominator
        else 0.0
    )

    true_merges = (
        true_positive_auto_merges
        + false_negative_auto_separations
        + review_on_true_merge
    )
    merge_recall = true_positive_auto_merges / true_merges if true_merges else 0.0
    merge_f1 = (
        2 * auto_merge_precision * merge_recall
        / (auto_merge_precision + merge_recall)
        if auto_merge_precision + merge_recall
        else 0.0
    )

    covered_accuracy = (
        (true_positive_auto_merges + true_negative_auto_separations) / covered
        if covered
        else 0.0
    )

    result = {
        "schema": "zsi.entity-resolution/holdout-results-2.0",
        "holdout": "holdout-v2.json",
        "resolver": "zsi_entity_resolver_v12.predict",
        "cases": total,
        "metrics": {
            "true_positive_auto_merges": true_positive_auto_merges,
            "false_positive_auto_merges": false_positive_auto_merges,
            "true_negative_auto_separations": true_negative_auto_separations,
            "false_negative_auto_separations": false_negative_auto_separations,
            "review_on_true_merge": review_on_true_merge,
            "review_on_true_separate": review_on_true_separate,
            "auto_merge_precision": round(auto_merge_precision, 4),
            "merge_recall_including_reviews": round(merge_recall, 4),
            "merge_f1_including_reviews": round(merge_f1, 4),
            "auto_decision_coverage": round(covered / total, 4),
            "covered_accuracy": round(covered_accuracy, 4),
            "review_rate": round(reviews / total, 4),
        },
        "errors": [
            row
            for row in rows
            if row["predicted"] != "review" and row["predicted"] != row["expected"]
        ],
        "reviews": [row for row in rows if row["predicted"] == "review"],
        "results": rows,
        "guardrail": (
            "First v12 evaluation on frozen holdout-v2. Do not tune on these "
            "outcomes and re-report v2 as unseen. A future resolver repair "
            "requires holdout-v3. This benchmark is developer-authored, not "
            "independent external validation."
        ),
    }

    OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
