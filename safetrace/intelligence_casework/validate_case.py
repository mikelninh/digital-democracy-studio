from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASE_PATH = ROOT / "data" / "case_v001.json"

ALLOWED_CLAIM_STATES = {
    "supported",
    "supported_with_gap",
    "contradicted",
    "negative_evidence",
    "unresolved",
}

CONSEQUENTIAL_RELATIONSHIPS = {"OWNS", "DIRECTOR_OF", "SAME_AS"}


def load_case() -> dict:
    return json.loads(CASE_PATH.read_text(encoding="utf-8"))


def validate(case: dict) -> list[str]:
    errors: list[str] = []

    entities = {item["id"]: item for item in case.get("entities", [])}
    sources = {item["id"]: item for item in case.get("sources", [])}
    claims = {item["id"]: item for item in case.get("claims", [])}

    if not case.get("client_question"):
        errors.append("case must have a bounded client_question")

    if "SYNTHETIC" not in case.get("classification", "").upper():
        errors.append("public training case must be explicitly classified as synthetic")

    if not entities:
        errors.append("case must contain entities")
    if not sources:
        errors.append("case must contain sources")
    if not claims:
        errors.append("case must contain claims")

    for source_id, source in sources.items():
        for field in ("title", "kind", "authority", "relevance", "freshness", "anchor", "hash", "status"):
            if not source.get(field):
                errors.append(f"{source_id}: missing source field {field}")

    for claim_id, claim in claims.items():
        state = claim.get("state")
        if state not in ALLOWED_CLAIM_STATES:
            errors.append(f"{claim_id}: unsupported claim state {state!r}")
        if not claim.get("text"):
            errors.append(f"{claim_id}: missing text")
        if not claim.get("limitation"):
            errors.append(f"{claim_id}: missing limitation")
        if not claim.get("support") and state != "unresolved":
            errors.append(f"{claim_id}: reviewed claim has no supporting source")
        for source_id in claim.get("support", []) + claim.get("contradict", []):
            if source_id not in sources:
                errors.append(f"{claim_id}: references unknown source {source_id}")

    for edge in case.get("relationships", []):
        edge_label = f"{edge.get('from')}->{edge.get('to')}:{edge.get('type')}"
        if edge.get("from") not in entities or edge.get("to") not in entities:
            errors.append(f"{edge_label}: references unknown entity")
        if edge.get("claim_id") not in claims:
            errors.append(f"{edge_label}: missing linked claim")
        if not edge.get("evidence"):
            errors.append(f"{edge_label}: relationship has no evidence")
        for source_id in edge.get("evidence", []):
            if source_id not in sources:
                errors.append(f"{edge_label}: references unknown source {source_id}")
        if edge.get("type") in CONSEQUENTIAL_RELATIONSHIPS and edge.get("confidence", 0) < 0.90:
            errors.append(f"{edge_label}: consequential relationship confidence below 0.90")

    screening = case.get("screening", {})
    if screening.get("same_as") is not False:
        errors.append("synthetic sanctions homonym must remain rejected as SAME_AS")
    if len(screening.get("reasons_against_merge", [])) < 2:
        errors.append("rejected screening merge needs multiple documented reasons")

    contradictions = case.get("contradictions", [])
    if not contradictions:
        errors.append("case must expose at least one contradiction")
    for item in contradictions:
        if item.get("source_a") not in sources or item.get("source_b") not in sources:
            errors.append(f"{item.get('id')}: contradiction references unknown source")
        if not item.get("next_step"):
            errors.append(f"{item.get('id')}: contradiction needs a next investigative step")

    questions = case.get("questions_remaining", [])
    priorities = [item.get("priority") for item in questions]
    if not priorities or priorities != sorted(priorities) or len(set(priorities)) != len(priorities):
        errors.append("remaining questions must have unique ascending priorities")
    for item in questions:
        if not item.get("best_source") or not item.get("why"):
            errors.append(f"priority {item.get('priority')}: missing why/best_source")

    controls = case.get("quality_controls", {})
    if controls.get("contradictions_visible") is not True:
        errors.append("quality control must keep contradictions visible")
    if controls.get("negative_evidence_bounded") is not True:
        errors.append("quality control must bound negative evidence")
    if controls.get("accusation_from_risk_signal") is not False:
        errors.append("risk signals must never auto-promote to accusations")

    # Case-specific analytical invariants.
    ownership = {(edge["from"], edge["to"]): edge.get("value") for edge in case.get("relationships", []) if edge.get("type") == "OWNS"}
    if ownership.get(("E2", "E1")) != "70%":
        errors.append("expected Meridian -> Northstar 70% ownership edge")
    if ownership.get(("E3", "E2")) != "60%":
        errors.append("expected Asterion -> Meridian 60% ownership edge")

    return errors


def main() -> int:
    case = load_case()
    errors = validate(case)
    if errors:
        print(f"FAIL: {len(errors)} intelligence-casework quality gate(s) failed")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS: V-001 satisfies intelligence-casework quality gates")
    print(f"  entities: {len(case['entities'])}")
    print(f"  relationships: {len(case['relationships'])}")
    print(f"  sources: {len(case['sources'])}")
    print(f"  claims: {len(case['claims'])}")
    print(f"  contradictions: {len(case['contradictions'])}")
    print(f"  open questions: {len(case['questions_remaining'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
