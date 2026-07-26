"""Fail-closed validation for SafeTrace v0.4 Portfolio Truth."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PORTFOLIO = ROOT / "active_portfolio_v0_4.json"
EXPECTED_IDS = {"CASE-015", "CASE-012", "CAND-033", "CAND-039", "CAND-045"}
NEED_KEYS = {"severity", "scale", "urgency", "vulnerability", "public_value", "overlookedness", "total"}
FEASIBILITY_KEYS = {"source_access", "falsifiability", "jurisdiction_clarity", "safety_legality", "capacity", "total"}


def fail(message: str) -> None:
    raise ValueError(message)


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_score(block: object, keys: set[str], maximum: int, case_id: str) -> None:
    if not isinstance(block, dict) or set(block) != keys:
        fail(f"{case_id}: invalid score block")
    components = [value for key, value in block.items() if key != "total"]
    if any(not isinstance(value, int) or not 0 <= value <= 5 for value in components):
        fail(f"{case_id}: score component outside 0-5")
    if block["total"] != sum(components) or not 0 <= block["total"] <= maximum:
        fail(f"{case_id}: score total mismatch")


def validate() -> dict[str, object]:
    data = json.loads(PORTFOLIO.read_text(encoding="utf-8"))
    if data.get("schema") != "safetrace.active-portfolio/0.4":
        fail("unexpected schema")
    capacity = data.get("capacity_rule")
    if not isinstance(capacity, dict) or capacity.get("active_limit") != 5 or capacity.get("active_count") != 5:
        fail("active portfolio must be capped at five")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) != 5:
        fail("portfolio must contain exactly five active cases")
    if {case.get("id") for case in cases if isinstance(case, dict)} != EXPECTED_IDS:
        fail("active case set differs from bounded portfolio decision")

    generated = date.fromisoformat(str(data["generated_at"]))
    single_source = 0
    review_required = 0
    for case in cases:
        if not isinstance(case, dict):
            fail("invalid case object")
        case_id = str(case.get("id"))
        for field in ("story_title", "research_question", "affected_group", "jurisdiction"):
            if not nonempty(case.get(field)):
                fail(f"{case_id}: missing {field}")
        validate_score(case.get("need"), NEED_KEYS, 30, case_id)
        validate_score(case.get("feasibility"), FEASIBILITY_KEYS, 25, case_id)

        evidence = case.get("evidence")
        if not isinstance(evidence, dict):
            fail(f"{case_id}: missing evidence")
        for field in ("verified_claims", "unknowns", "counterevidence", "sources"):
            values = evidence.get(field)
            if not isinstance(values, list) or not values:
                fail(f"{case_id}: evidence.{field} must be non-empty")
        if len(evidence["sources"]) == 1:
            single_source += 1
        for source in evidence["sources"]:
            if not isinstance(source, dict):
                fail(f"{case_id}: invalid source")
            for field in ("source_id", "publisher", "title", "date", "url", "receipt_status"):
                if not nonempty(source.get(field)):
                    fail(f"{case_id}: source missing {field}")
            parsed = urlparse(source["url"])
            if parsed.scheme != "https" or not parsed.netloc:
                fail(f"{case_id}: source must use HTTPS")
            if source["receipt_status"] not in {"url_only", "snapshot_retained", "hashed_and_reviewed"}:
                fail(f"{case_id}: invalid source receipt status")

        fairness = case.get("fairness")
        if not isinstance(fairness, dict) or not nonempty(fairness.get("strongest_counterposition")):
            fail(f"{case_id}: missing strongest counterposition")
        if not fairness.get("alternative_explanations"):
            fail(f"{case_id}: missing alternative explanations")
        if fairness.get("right_of_reply") != "required_not_sent":
            fail(f"{case_id}: initial right-of-reply state must be explicit")

        action = case.get("action_contract")
        if not isinstance(action, dict):
            fail(f"{case_id}: missing action contract")
        for field in ("target_actor", "exact_ask", "internal_owner", "deliverable", "stop_condition"):
            if not nonempty(action.get(field)):
                fail(f"{case_id}: action contract missing {field}")
        deadline = date.fromisoformat(str(action.get("deadline")))
        if deadline < generated:
            fail(f"{case_id}: deadline predates portfolio generation")
        if not isinstance(action.get("safe_citizen_actions"), list) or not action["safe_citizen_actions"]:
            fail(f"{case_id}: safe citizen actions required")

        impact = case.get("impact_contract")
        if not isinstance(impact, dict) or impact.get("status") != "complete":
            fail(f"{case_id}: complete impact contract required")
        for field in ("metric", "baseline", "target", "data_source", "owner", "cadence", "attribution_rule"):
            if impact.get(field) in (None, ""):
                fail(f"{case_id}: impact contract missing {field}")
        if impact.get("level") not in {"reach", "evidence", "accountability", "system", "outcome"}:
            fail(f"{case_id}: invalid impact level")

        publication = case.get("publication")
        if not isinstance(publication, dict) or publication.get("readiness") not in {"scoping", "review_required"}:
            fail(f"{case_id}: unsafe publication readiness")
        if publication.get("readiness") == "review_required":
            review_required += 1
        if case.get("lifecycle") != "active_sprint":
            fail(f"{case_id}: active portfolio case must be active_sprint")

    return {
        "status": "valid",
        "active_cases": len(cases),
        "active_limit": capacity["active_limit"],
        "cases_with_owner": len(cases),
        "cases_with_deadline_and_stop_condition": len(cases),
        "complete_impact_contracts": len(cases),
        "single_source_cases": single_source,
        "review_required_cases": review_required,
        "automatic_publication_enabled": False,
        "confidential_intake_enabled": False,
    }


def main() -> int:
    try:
        result = validate()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "invalid", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
