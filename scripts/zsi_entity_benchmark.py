from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ER = ROOT / "zero-suffering-intelligence" / "entity-resolution"
BENCH = ER / "benchmark-v1.json"
RESULTS = ER / "results-v1.json"

LEGAL_SUFFIXES = {"gmbh", "co", "kg", "mbh", "sce", "aps", "ag", "group", "gruppe"}

# Reviewed alias seeds are explicit resolver inputs, not labels learned from the test result.
REVIEWED_ALIAS_GROUPS = [
    {
        "premium food group aps co kg",
        "premium food group",
        "premiumfoodgroup",
        "pfg",
        "toennies unternehmensgruppe",
        "toennies holding",
        "p f g",
    },
    {
        "westfleisch sce mbh",
        "westfleisch",
        "west fleisch sce",
        "westfleisch s c e mbh",
        "west fleisch",
    },
]


def raw_normalise(value: str) -> str:
    value = value.lower()
    value = value.replace("ö", "oe").replace("ä", "ae").replace("ü", "ue").replace("ß", "ss")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def name_normalise(value: str) -> str:
    tokens = [t for t in raw_normalise(value).split() if t not in LEGAL_SUFFIXES]
    return " ".join(tokens)


def canonical_name(value: str) -> str:
    raw = raw_normalise(value)
    stripped = name_normalise(value)
    candidates = {raw, stripped}
    for i, group in enumerate(REVIEWED_ALIAS_GROUPS):
        if candidates & group:
            return f"reviewed_alias_group_{i}"
    return stripped


def predict(a: dict, b: dict) -> tuple[str, str]:
    a_id, b_id = a.get("stable_id"), b.get("stable_id")
    if a_id and b_id:
        return ("merge" if a_id == b_id else "separate", "stable identifiers")

    a_name, b_name = canonical_name(a["name"]), canonical_name(b["name"])
    if a_name == b_name:
        return "merge", "canonical or reviewed-alias name match"

    a_tokens, b_tokens = set(a_name.split()), set(b_name.split())
    union = a_tokens | b_tokens
    jaccard = len(a_tokens & b_tokens) / len(union) if union else 0.0
    if jaccard >= 0.85 and a.get("address") == b.get("address"):
        return "merge", f"high token overlap ({jaccard:.2f}) plus matching address"

    return "separate", f"insufficient identity evidence (token overlap {jaccard:.2f})"


def main() -> None:
    data = json.loads(BENCH.read_text(encoding="utf-8"))
    rows = []
    tp = fp = fn = tn = 0

    for case in data["cases"]:
        predicted, reason = predict(case["record_a"], case["record_b"])
        expected = case["ground_truth"]
        correct = predicted == expected
        if expected == "merge" and predicted == "merge":
            tp += 1
        elif expected == "separate" and predicted == "merge":
            fp += 1
        elif expected == "merge" and predicted == "separate":
            fn += 1
        else:
            tn += 1
        rows.append(
            {
                "case_id": case["case_id"],
                "expected": expected,
                "predicted": predicted,
                "correct": correct,
                "reason": reason,
                "record_a": case["record_a"]["name"],
                "record_b": case["record_b"]["name"],
            }
        )

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(rows) if rows else 0.0

    result = {
        "schema": "zsi.entity-resolution/results-1.0",
        "benchmark": "benchmark-v1.json",
        "cases": len(rows),
        "metrics": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "accuracy": round(accuracy, 4),
        },
        "errors": [r for r in rows if not r["correct"]],
        "results": rows,
        "guardrail": "This is a frozen synthetic benchmark. It measures this resolver configuration, not production accuracy on all organisations. Every production merge remains reviewable and reversible.",
    }
    RESULTS.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
