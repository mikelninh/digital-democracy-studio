from pathlib import Path
import json

import engine
from claim_ledger import Claim, EvidenceReceipt, contradiction_pairs, explain_claim

ROOT = Path(__file__).parent
ontology = json.loads((ROOT / "ontology.json").read_text(encoding="utf-8"))
golden = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run() -> None:
    cases = golden["cases"]
    check(len(cases) >= 12, "expected at least 12 golden cases")
    ids = [case["id"] for case in cases]
    check(len(ids) == len(set(ids)), "golden case ids must be unique")

    allowed_types = set(ontology["entity_types"])
    for case in cases:
        expected = case["expected"]
        unknown = set(expected["entity_types"]) - allowed_types
        check(not unknown, f"{case['id']} uses unknown entity types: {unknown}")
        check(bool(expected["capabilities"]), f"{case['id']} needs capabilities")
        check(bool(case["modules"]), f"{case['id']} needs module mapping")
        check(bool(case["must_not"]), f"{case['id']} needs explicit negative boundaries")
        check(bool(expected["uncertainty"]), f"{case['id']} must expose uncertainty")

    sensitive_cases = [case for case in cases if case["expected"]["human_review"]]
    for case in sensitive_cases:
        plan = engine.build_plan(case["question"])
        check(plan["autonomous_action_allowed"] is False, f"{case['id']} crossed human approval boundary")

    probes = {
        "My Wohngeld was rejected. What can I do?": "citizen-wohngeld-rejection",
        "Are these suppliers actually the same entity or linked by a director?": "investigator-supplier-links",
        "Where did the public money for this programme go?": "investigator-public-money",
        "Which authority is responsible for this problem?": "citizen-authority-responsibility",
        "A rule changed. Which services are affected?": "operator-policy-change-impact"
    }
    for question, case_id in probes.items():
        plan = engine.build_plan(question)
        check(plan.get("matched_case") == case_id, f"wrong workflow match for: {question}")

    fallback = engine.build_plan("Can you decide this completely unknown consequential matter for me?")
    check(fallback["status"] == "insufficient_grounding", "unknown questions must fail bounded")
    check(fallback["human_review"] is True, "unknown consequential questions must escalate")
    check(fallback["autonomous_action_allowed"] is False, "fallback may not act")

    receipt = EvidenceReceipt(
        id="ev-1",
        source="synthetic://registry/a",
        source_type="registry",
        retrieved_at="2026-08-28T00:00:00+00:00"
    )
    claim_a = Claim(
        id="claim-a", subject_id="org-1", predicate="DIRECTOR_OF", object_id="person-a",
        status="supported", evidence_ids=("ev-1",), valid_from="2026-01-01", confidence=0.9
    )
    claim_b = Claim(
        id="claim-b", subject_id="org-1", predicate="DIRECTOR_OF", object_id="person-b",
        status="unresolved", evidence_ids=("ev-2",), valid_from="2026-01-01", confidence=0.7
    )
    conflicts = contradiction_pairs([claim_a, claim_b])
    check(len(conflicts) == 1, "overlapping contradictory claims must be surfaced")
    check(conflicts[0]["review_state"] == "human_review_required", "contradiction must escalate")

    explained = explain_claim(claim_a, [receipt])
    check(len(explained["evidence"]) == 1, "claim must resolve its evidence receipt")
    check(not explained["missing_evidence_ids"], "supported proof fixture must have no missing receipt")

    print(f"PASS: {len(cases)} golden cases validated")
    print("PASS: ontology contract")
    print("PASS: human-approval boundaries")
    print("PASS: deterministic workflow probes")
    print("PASS: insufficient-grounding fallback")
    print("PASS: claim ledger evidence receipts")
    print("PASS: temporal contradiction escalation")


if __name__ == "__main__":
    run()
