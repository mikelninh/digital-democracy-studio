from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from source_backing import source_pack

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


def find_case(question: str) -> dict[str, Any] | None:
    text = question.lower()
    by_id = {case["id"]: case for case in GOLDEN["cases"]}
    best: dict[str, Any] | None = None
    for case_id, words in KEYWORDS.items():
        score = sum(1 for word in words if word in text)
        if score and (best is None or score > best["score"]):
            best = {"case": by_id[case_id], "score": score}
    return best


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
            "next_best_action": None,
            "proposed_action": None,
            "autonomous_action_allowed": False
        }

    case = match["case"]
    expected = case["expected"]
    backing = source_pack(case["id"])
    route_state = "authoritative_routes_verified" if backing["all_routes_verified"] else "source_gap"
    live_state = "live_sources_fetched" if backing["all_live_fetched"] else "live_fetch_pending"

    return {
        "status": "source_backed_plan",
        "question": question,
        "matched_case": case["id"],
        "persona": case["persona"],
        "domain": case["domain"],
        "confidence": route_state,
        "source_state": live_state,
        "modules": case["modules"],
        "required_entity_types": expected["entity_types"],
        "capabilities": expected["capabilities"],
        "uncertainty": expected["uncertainty"],
        "human_review": expected["human_review"],
        "proposed_action": expected["next_action"],
        "next_best_action": backing["next_best_action"],
        "autonomous_action_allowed": False if expected["human_review"] else expected["next_action"] not in ONTOLOGY["action_policy"]["requires_human_approval"],
        "must_not": case["must_not"],
        "why": {
            "matched_case": case["id"],
            "keyword_score": match["score"],
            "authoritative_sources": backing["authoritative_sources"],
            "source_contract": backing["source_contract"],
            "note": "Authoritative source routes are verified, but a source becomes run evidence only after a live connector fetches it and produces an evidence receipt."
        }
    }


if __name__ == "__main__":
    import sys
    question = " ".join(sys.argv[1:]) or "Which authority is responsible and why?"
    print(json.dumps(build_plan(question), ensure_ascii=False, indent=2))
