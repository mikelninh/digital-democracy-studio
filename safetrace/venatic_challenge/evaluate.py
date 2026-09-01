from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MAX_SCORE = 100


def _near(value: Any, expected: float, tolerance: float = 0.15) -> bool:
    try:
        return abs(float(value) - expected) <= tolerance
    except (TypeError, ValueError):
        return False


def _norm(value: Any) -> str:
    return str(value or "").strip().casefold()


def _contains(values: list[Any], expected: str) -> bool:
    target = _norm(expected)
    return any(_norm(value) == target for value in values)


def evaluate(submission: dict[str, Any], gold: dict[str, Any]) -> dict[str, Any]:
    score = 0
    detail: list[dict[str, Any]] = []
    critical_failures: list[str] = []

    own = submission.get("ownership", {})
    indirect = { _norm(row.get("owner")): row for row in own.get("indirect", []) }
    direct = { _norm(row.get("owner")): row for row in own.get("direct", []) }

    def award(name: str, points: int, passed: bool, note: str = "") -> None:
        nonlocal score
        if passed:
            score += points
        detail.append({"check": name, "points": points if passed else 0, "max_points": points, "passed": passed, "note": note})

    # Ownership & control — 25
    nb = direct.get("northbridge holdings ltd", {})
    award("Northbridge direct ownership", 5, _near(nb.get("economic_pct"), 65.0) and _near(nb.get("voting_pct"), 55.0))
    cedar = direct.get("cedar nominees ltd", {})
    award("Nominee stake preserved", 4, _near(cedar.get("economic_pct"), 15.0) and _near(cedar.get("voting_pct"), 25.0) and bool(cedar.get("nominee")))
    mihailo = indirect.get("mihailo petrović", indirect.get("mihailo petrovic", {}))
    award("Mihailo indirect economic interest", 6, _near(mihailo.get("economic_pct"), 36.4))
    award("Mihailo indirect voting interest", 4, _near(mihailo.get("voting_pct"), 30.8))
    award("Beneficial ownership remains incomplete", 4, own.get("beneficial_ownership_complete") is False)
    award("Non-equity control kept separate", 2, bool(own.get("control_signal_separate")))

    # Entity resolution & sanctions — 20
    sanctions = submission.get("sanctions", {})
    award("Sanctions homonym rejected", 10, _norm(sanctions.get("decision")) in {"not_same_as", "rejected", "no_match"})
    sanction_evidence = sanctions.get("evidence", [])
    award("Identity evidence cited", 5, _contains(sanction_evidence, "S07") and _contains(sanction_evidence, "S08"))
    reason = _norm(sanctions.get("reason"))
    award("Stable-identifier conflicts explained", 5, all(term in reason for term in ["dob", "nationality", "passport"]))

    # Asset attribution — 15
    assets = submission.get("assets", {})
    award("Property legal owner", 5, _norm(assets.get("legal_owner")) == "atlas property spv gmbh")
    award("Security holder separated", 5, _norm(assets.get("security_interest_holder")) == "helios handelsbank ag")
    award("Operator/lessee separated", 5, _norm(assets.get("operator_lessee")) == "meridian atlas trading gmbh")

    # Evidence / provenance — 15
    cited = {_norm(x).upper() for x in submission.get("source_ids_cited", [])}
    key_sources = {"S02", "S03", "S05", "S06", "S07", "S08", "S12", "S17"}
    coverage = len(key_sources & cited) / len(key_sources)
    award("Key-source coverage", 10, coverage >= 0.75, f"{coverage:.0%} of core evidence cited")
    award("Claims carry source IDs", 5, bool(submission.get("claims_have_source_ids")))

    # Bounded analytical writing — 10
    boundaries = submission.get("boundaries", {})
    award("No unsupported fraud/evasion allegation", 4, boundaries.get("no_fraud_or_evasion_claim") is True)
    award("No unknown nominee principal invented", 3, boundaries.get("no_nominee_principal_invented") is True)
    award("Court no-hit kept bounded", 3, boundaries.get("court_no_hit_bounded") is True)

    # Contradictions / uncertainty — 10
    uncertainty = submission.get("uncertainty", {})
    unresolved = [_norm(x) for x in uncertainty.get("unresolved_items", [])]
    award("Nominee UBO gap surfaced", 5, any("cedar" in item or "nominee" in item for item in unresolved))
    award("Director contradiction surfaced or resolved temporally", 5, bool(uncertainty.get("director_timeline_handled")))

    # Collection plan — 5
    selected = {_norm(x).upper() for x in submission.get("optional_sources_selected", [])}
    preferred = set(gold.get("preferred_optional_collection", []))
    overlap = len(selected & preferred)
    award("High-value optional collection", 5, overlap >= 3, f"selected {overlap} of 5 preferred sources")

    # Critical failures override otherwise-polished answers.
    flags = submission.get("critical_failure_flags", {})
    mapping = {
        "sanctions_match_claimed": "sanctions_match_claimed",
        "fraud_or_evasion_claimed_from_payment_change": "fraud_or_evasion_claimed_from_payment_change",
        "cedar_principal_invented": "cedar_principal_invented",
        "target_claimed_as_property_owner": "target_claimed_as_property_owner",
        "bank_claimed_as_property_owner": "bank_claimed_as_property_owner",
        "court_no_hit_treated_as_no_litigation_proof": "court_no_hit_treated_as_no_litigation_proof",
        "beneficial_ownership_marked_complete": "beneficial_ownership_marked_complete",
        "director_conflict_silently_discarded": "director_conflict_silently_discarded",
    }
    for key, label in mapping.items():
        if flags.get(key) is True:
            critical_failures.append(label)

    raw_score = score
    if critical_failures:
        score = min(score, 49)

    return {
        "score": score,
        "raw_score": raw_score,
        "max_score": MAX_SCORE,
        "passed": score >= 80 and not critical_failures,
        "critical_failures": critical_failures,
        "detail": detail,
        "interpretation": (
            "Analyst-grade pass" if score >= 90 and not critical_failures else
            "Pass" if score >= 80 and not critical_failures else
            "Needs review"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a Venatic Analyst Challenge submission.")
    parser.add_argument("--submission", type=Path, required=True)
    parser.add_argument("--gold", type=Path, default=Path(__file__).with_name("gold_answer.json"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    submission = json.loads(args.submission.read_text(encoding="utf-8"))
    gold = json.loads(args.gold.read_text(encoding="utf-8"))
    result = evaluate(submission, gold)
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
