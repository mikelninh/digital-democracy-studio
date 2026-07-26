"""Transparent prioritisation for Spuren im System case proposals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "cases.json"

DIMENSIONS = (
    "harm",
    "evidence_access",
    "actionability",
    "urgency",
    "public_value",
    "fairness_capacity",
)

PENALTIES = {
    "private_data": 6,
    "unsafe_methods": 12,
    "unclear_question": 6,
    "capacity_gap": 4,
}


def decision_for(score: int) -> str:
    if score >= 24:
        return "priorisiert_annehmen"
    if score >= 18:
        return "datensprint_definieren"
    if score >= 12:
        return "vorpruefung_oder_frage_schaerfen"
    return "nicht_annehmen_oder_weiterverweisen"


def compute_score(dimensions: Mapping[str, int], penalties: Mapping[str, int]) -> int:
    for name in DIMENSIONS:
        value = dimensions.get(name)
        if not isinstance(value, int) or not 0 <= value <= 5:
            raise ValueError(f"{name} must be an integer from 0 to 5")
    score = sum(dimensions[name] for name in DIMENSIONS)
    for name, maximum in PENALTIES.items():
        value = penalties.get(name, 0)
        if not isinstance(value, int) or not 0 <= value <= maximum:
            raise ValueError(f"{name} penalty must be an integer from 0 to {maximum}")
        score -= value
    return max(0, score)


def validate_catalog() -> list[dict[str, object]]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    ranked: list[dict[str, object]] = []
    for case in data["cases"]:
        priority = case["priority"]
        dims = {name: priority[name] for name in DIMENSIONS}
        calculated = compute_score(dims, priority["penalties"])
        if calculated != priority["total"]:
            raise ValueError(
                f"{case['id']} priority total is {priority['total']}, expected {calculated}"
            )
        expected_decision = decision_for(calculated)
        if priority["decision"] != expected_decision:
            raise ValueError(
                f"{case['id']} decision is {priority['decision']}, expected {expected_decision}"
            )
        ranked.append(
            {
                "case_id": case["id"],
                "story_title": case["story_title"],
                "score": calculated,
                "decision": expected_decision,
                "publication_readiness": case["publication_readiness"],
                "urgency": priority["urgency"],
                "evidence_access": priority["evidence_access"],
            }
        )
    return sorted(
        ranked,
        key=lambda item: (
            -int(item["score"]),
            -int(item["urgency"]),
            -int(item["evidence_access"]),
            str(item["case_id"]),
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text")
    args = parser.parse_args()

    try:
        ranked = validate_catalog()
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False))
        return 1

    if args.json:
        print(json.dumps({"status": "valid", "ranking": ranked}, ensure_ascii=False, indent=2))
    else:
        for index, item in enumerate(ranked, start=1):
            print(
                f"{index}. {item['case_id']} — {item['story_title']}: "
                f"{item['score']}/30 · {item['decision']} · "
                f"{item['publication_readiness']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
