from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASE_PATH = ROOT / "data" / "case_v001.json"
EVAL_PATH = ROOT / "data" / "analyst_eval_v001.json"
ASSET_PATH = ROOT / "data" / "asset_trace_v001.json"

ALLOWED_CLAIM_STATES = {
    "supported",
    "supported_with_gap",
    "contradicted",
    "negative_evidence",
    "unresolved",
}

CONSEQUENTIAL_RELATIONSHIPS = {"OWNS", "DIRECTOR_OF", "SAME_AS"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_case() -> dict:
    return load_json(CASE_PATH)


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
    ownership = {
        (edge["from"], edge["to"]): edge.get("value")
        for edge in case.get("relationships", [])
        if edge.get("type") == "OWNS"
    }
    if ownership.get(("E2", "E1")) != "70%":
        errors.append("expected Meridian -> Northstar 70% ownership edge")
    if ownership.get(("E3", "E2")) != "60%":
        errors.append("expected Asterion -> Meridian 60% ownership edge")

    return errors


def validate_eval(evaluation: dict, case: dict) -> list[str]:
    errors: list[str] = []
    source_ids = {item["id"] for item in case.get("sources", [])}
    items = evaluation.get("items", [])
    scoring = evaluation.get("scoring", {})

    if "SYNTHETIC" not in evaluation.get("classification", "").upper():
        errors.append("analyst evaluation must be explicitly synthetic")
    if len(items) != 10:
        errors.append("analyst evaluation must contain exactly 10 gold items")
    if scoring.get("total_points") != 100 or scoring.get("points_per_item") != 10:
        errors.append("analyst evaluation must remain a 100-point scorecard")
    if scoring.get("pass_threshold", 0) < 80:
        errors.append("analyst evaluation pass threshold must be at least 80")
    if len(scoring.get("critical_fail_rules", [])) < 4:
        errors.append("analyst evaluation needs explicit critical-fail rules")

    for item in items:
        item_id = item.get("id", "unknown")
        for field in ("question", "gold_answer", "required_sources", "required_concepts", "forbidden_inference"):
            if not item.get(field):
                errors.append(f"{item_id}: missing evaluation field {field}")
        for source_id in item.get("required_sources", []):
            if source_id not in source_ids:
                errors.append(f"{item_id}: unknown required source {source_id}")

    return errors


def validate_asset_trace(asset_trace: dict) -> list[str]:
    errors: list[str] = []
    assets = {item["asset_id"]: item for item in asset_trace.get("assets", [])}
    parties = {item["id"]: item for item in asset_trace.get("parties", [])}
    sources = {item["id"]: item for item in asset_trace.get("sources", [])}
    interests = asset_trace.get("interests", [])

    if "SYNTHETIC" not in asset_trace.get("classification", "").upper():
        errors.append("asset trace must be explicitly synthetic")
    if len(assets) < 2:
        errors.append("asset trace must exercise at least two asset types")

    interest_types = {item.get("type") for item in interests}
    required_types = {"LEGAL_OWNER_OF", "SECURITY_INTEREST_IN", "OPERATES_AT", "LESSEE_OF"}
    if not required_types.issubset(interest_types):
        errors.append("asset trace must distinguish ownership, security, operation and lease interests")

    for interest in interests:
        label = f"{interest.get('from')}->{interest.get('to')}:{interest.get('type')}"
        if interest.get("from") not in parties:
            errors.append(f"{label}: unknown party")
        if interest.get("to") not in assets:
            errors.append(f"{label}: unknown asset")
        if interest.get("confidence", 0) < 0.90:
            errors.append(f"{label}: material asset interest confidence below 0.90")
        if not interest.get("assessment") or not interest.get("evidence"):
            errors.append(f"{label}: missing assessment/evidence")
        for source_id in interest.get("evidence", []):
            if source_id not in sources:
                errors.append(f"{label}: unknown asset source {source_id}")

    guardrails = " ".join(asset_trace.get("guardrails", [])).lower()
    for concept in ("use or possession", "security interest", "corporate group", "as-of"):
        if concept not in guardrails:
            errors.append(f"asset trace guardrail missing concept: {concept}")

    return errors


def main() -> int:
    case = load_case()
    evaluation = load_json(EVAL_PATH)
    asset_trace = load_json(ASSET_PATH)
    errors = validate(case) + validate_eval(evaluation, case) + validate_asset_trace(asset_trace)

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
    print(f"  analyst eval items: {len(evaluation['items'])}")
    print(f"  traced assets: {len(asset_trace['assets'])}")
    print(f"  asset interests: {len(asset_trace['interests'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
