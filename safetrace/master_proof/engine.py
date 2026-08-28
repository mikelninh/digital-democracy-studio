from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
ONTOLOGY = json.loads((ROOT / "ontology.json").read_text(encoding="utf-8"))
GOLDEN = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))

KEYWORDS = {
    "citizen-wohngeld-rejection": ["wohngeld", "housing benefit", "rejected", "abgelehnt"],
    "citizen-benefits-gap": ["benefit", "leistungen", "support", "unterstützung", "anspruch"],
    "citizen-rent-increase": ["rent", "miete", "mieterhöhung", "landlord"],
    "citizen-digital-harassment": ["harass", "beläst", "online", "digital violence"],
    "citizen-authority-responsibility": ["authority", "behörde", "zuständig", "responsible"],
    "citizen-information-request": ["information request", "informationsfrei", "transparency", "auskunft"],
    "investigator-supplier-links": ["supplier", "vendor", "same entity", "director", "lieferant"],
    "investigator-public-money": ["public money", "budget", "funding", "haushalt", "förder"],
    "investigator-procurement-pattern": ["procurement", "contract", "tender", "vergabe", "auftrag"],
    "investigator-contradictory-records": ["disagree", "contradict", "widerspruch", "records"],
    "operator-permit-routing": ["permit", "genehmigung", "department", "blocked"],
    "operator-policy-change-impact": ["rule changed", "law changed", "gesetz geändert", "impact"]
}


@dataclass(frozen=True)
class Match:
    case: dict[str, Any]
    score: int


def find_case(question: str) -> Match | None:
    text = question.lower()
    ranked: list[Match] = []
    by_id = {case["id"]: case for case in GOLDEN["cases"]}
    for case_id, words in KEYWORDS.items():
        score = sum(1 for word in words if word in text)
        if score:
            ranked.append(Match(by_id[case_id], score))
    return max(ranked, key=lambda item: item.score, default=None)


def build_plan(question: str) -> dict[str, Any]:
    match = find_case(question)
    if not match:
        return {
            "status": "insufficient_grounding",
            "question": question,
            "confidence": "low",
            "human_review": True,
            "answer": "No golden workflow matched strongly enough. Gather authoritative sources before proposing an action.",
            "why": {"matched_case": None, "evidence": [], "missing": ["grounded workflow"]},
            "proposed_action": None,
            "autonomous_action_allowed": False
        }

    case = match.case
    expected = case["expected"]
    prohibited = case["must_not"]
    return {
        "status": "bounded_plan",
        "question": question,
        "matched_case": case["id"],
        "persona": case["persona"],
        "domain": case["domain"],
        "confidence": "workflow-match-only",
        "modules": case["modules"],
        "required_entity_types": expected["entity_types"],
        "capabilities": expected["capabilities"],
        "uncertainty": expected["uncertainty"],
        "human_review": expected["human_review"],
        "proposed_action": expected["next_action"],
        "autonomous_action_allowed": False if expected["human_review"] else expected["next_action"] not in ONTOLOGY["action_policy"]["requires_human_approval"],
        "must_not": prohibited,
        "why": {
            "matched_case": case["id"],
            "keyword_score": match.score,
            "evidence": [],
            "note": "This layer selects the workflow only. Domain modules must attach source-backed evidence receipts before factual claims are promoted to supported."
        }
    }


if __name__ == "__main__":
    import sys
    question = " ".join(sys.argv[1:]) or "Which authority is responsible and why?"
    print(json.dumps(build_plan(question), ensure_ascii=False, indent=2))
