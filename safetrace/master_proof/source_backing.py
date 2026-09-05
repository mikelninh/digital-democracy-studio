from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
REGISTRY = json.loads((ROOT / "source_registry.json").read_text(encoding="utf-8"))
SNAPSHOTS = json.loads((ROOT / "source_snapshots.json").read_text(encoding="utf-8"))
GOLDEN = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))
CASES = {case["id"]: case for case in GOLDEN["cases"]}

NEXT_ACTIONS: dict[str, dict[str, Any]] = {
    "citizen-wohngeld-rejection": {"label": "Check the rejection against the facts and preserve the review deadline", "why": "The official Berlin service identifies the responsible housing office, legal bases and application facts; the rejection notice itself is still needed to determine the actual deadline and reason.", "needs": ["rejection notice", "application facts", "supporting documents"], "output": "review checklist + missing-evidence list + draft for human review"},
    "citizen-benefits-gap": {"label": "Run official pre-checks for the highest-probability support first", "why": "Wohngeld and Kinderzuschlag have official eligibility/application routes and can unlock related support; a household-specific conclusion still needs current facts.", "needs": ["household size", "income", "housing costs", "children/ages", "existing benefits"], "output": "ranked benefit checks + required documents + official routes"},
    "citizen-rent-increase": {"label": "Extract the rent-increase basis and compare it with the current statutory checks", "why": "BGB § 558 sets core timing and comparison-rent constraints, but the exact route depends on the landlord's stated legal basis and local/property facts.", "needs": ["rent increase letter", "current rent", "last increase date", "property facts"], "output": "fact matrix + statutory checks + reviewable response draft"},
    "citizen-digital-harassment": {"label": "Preserve complete evidence before content disappears or is reported", "why": "Police guidance prioritises preserving messages, context, dates, usernames and URLs; urgent threats should be escalated to police rather than handled by an agent.", "needs": ["original messages/URLs", "timestamps", "platform context"], "output": "hashed evidence package + safety options + human-reviewed reporting pack"},
    "citizen-authority-responsibility": {"label": "Resolve the service and jurisdiction in the official service directory", "why": "Responsibility depends on the service, location and current administrative allocation; the ServicePortal is the authoritative routing surface for Berlin services.", "needs": ["location", "problem/service type"], "output": "responsible body + official contact route + evidence-backed Why? path"},
    "citizen-information-request": {"label": "Identify the record-holding authority and prepare a narrow information request", "why": "Berlin IFG guidance allows requests to the record-holding body and recommends identifying the relevant file/record; access and exceptions remain case-specific.", "needs": ["decision/topic", "likely authority", "time period", "records sought"], "output": "reviewable request + authority route + exceptions warning"},
    "investigator-supplier-links": {"label": "Resolve legal identities first, then show relationship evidence separately", "why": "The Unternehmensregister provides current/chronological/historical register records and the Transparenzregister can support ownership/control checks; related entities must not be collapsed into SAME_AS.", "needs": ["supplier names", "addresses/domains/directors", "relevant dates"], "output": "canonical entities + supported links + ambiguous review queue"},
    "investigator-public-money": {"label": "Trace the programme from budget title to recipient-level evidence before flagging anomalies", "why": "Bundeshaushalt provides federal budget structure and machine-readable downloads while Bundesrechnungshof publications provide audit context; recipient-level links require additional programme/payment sources.", "needs": ["programme/title", "year", "spending authority", "recipient/payment source"], "output": "funding graph + evidence receipts + unresolved recipient gaps + follow-up questions"},
    "investigator-procurement-pattern": {"label": "Normalise vendors and compare awards over time before interpreting concentration", "why": "Berlin's procurement platform publishes current notices and awarded-contract information; company registers provide identity/control evidence. Repeated awards alone do not establish wrongdoing.", "needs": ["contract notices/awards", "vendor identifiers", "date range", "procurement category"], "output": "reproducible award pattern + entity graph + counterevidence + missing-data list"},
    "investigator-contradictory-records": {"label": "Build a dated claim timeline and keep both records visible until authoritative evidence resolves the conflict", "why": "Current, chronological and historical company-register extracts can distinguish changes over time; beneficial-control information may require a separate access route.", "needs": ["both records", "effective dates", "registry identifiers"], "output": "competing claims + temporal evidence + contradiction object + review requirement"},
    "operator-permit-routing": {"label": "Resolve the exact service bundle and show the first missing requirement blocking the case", "why": "Berlin's official service pages specify district responsibility, documents and legal bases for tree-protection and street special-use permissions; final approval remains with authorised officials.", "needs": ["project location", "project description", "tree/site facts", "submitted documents"], "output": "responsibility graph + evidence checklist + first blocker + internal next step"},
    "operator-policy-change-impact": {"label": "Verify the promulgated change, diff affected provisions, then queue potentially affected workflows for review", "why": "Gesetze im Internet provides a near-daily update feed linked to newly promulgated federal provisions; case impact remains a hypothesis until facts and effective dates are checked.", "needs": ["changed law/provision", "effective date", "service-to-rule mappings", "open cases"], "output": "legal diff + impact graph + prioritised human-review queue"}
}

LIVE_CONNECTOR_STATUS: dict[str, bool] = {source_id: False for source_id in REGISTRY["sources"]}


def source_pack(case_id: str) -> dict[str, Any]:
    if case_id not in CASES:
        raise KeyError(case_id)
    ids = REGISTRY["case_sources"].get(case_id, [])
    sources = []
    for source_id in ids:
        source = dict(REGISTRY["sources"][source_id])
        snapshot = SNAPSHOTS["snapshots"].get(source_id)
        source["id"] = source_id
        source["route_verified_at"] = REGISTRY["verified_at"]
        source["snapshot_retrieved_at"] = SNAPSHOTS["retrieved_at"] if snapshot else None
        source["snapshot_facts"] = snapshot["facts"] if snapshot else []
        if LIVE_CONNECTOR_STATUS[source_id]:
            source["backing_state"] = "live_fetch"
        elif snapshot:
            source["backing_state"] = "verified_snapshot"
        else:
            source["backing_state"] = "verified_route"
        sources.append(source)
    action = NEXT_ACTIONS[case_id]
    return {
        "case_id": case_id,
        "authoritative_sources": sources,
        "source_count": len(sources),
        "all_routes_verified": bool(sources),
        "all_have_snapshots": bool(sources) and all(s["snapshot_facts"] for s in sources),
        "all_live_fetched": bool(sources) and all(s["backing_state"] == "live_fetch" for s in sources),
        "next_best_action": action,
        "source_contract": {
            **REGISTRY["contract"],
            "verified_snapshot": "A dated, manually verified snapshot records supported facts for the master proof. It is evidence for that retrieval date, not a promise that the source is unchanged now.",
            "snapshot_warning": SNAPSHOTS["warning"]
        }
    }


def build_gap_audit() -> dict[str, Any]:
    cases = []
    for case_id in CASES:
        pack = source_pack(case_id)
        gaps: list[str] = []
        if not pack["all_live_fetched"]:
            gaps.append("execute allowlisted live fetch per run + retain raw source in reviewed Evidence Vault")
        if case_id in {"citizen-wohngeld-rejection", "citizen-rent-increase", "citizen-digital-harassment"}:
            gaps.append("production encrypted evidence storage + IAM + deletion/retention jobs + redaction UX")
        if case_id == "citizen-benefits-gap":
            gaps.append("verify/update benefit calculators against current-year official parameters before numeric entitlement output")
        if case_id in {"investigator-supplier-links", "investigator-contradictory-records"}:
            gaps.append("authenticated/terms-compliant register retrieval where access requires it")
        if case_id in {"investigator-public-money", "investigator-procurement-pattern"}:
            gaps.append("recipient/award normalisation and durable cross-source identifiers")
        if case_id == "operator-policy-change-impact":
            gaps.append("expand rule-to-service dependency coverage + parse promulgation/effective dates automatically")
        cases.append({"case_id": case_id, "source_routes_verified": pack["all_routes_verified"], "source_snapshots_present": pack["all_have_snapshots"], "live_fetched": pack["all_live_fetched"], "gaps": gaps, "gap_count": len(gaps)})

    ranked: dict[str, int] = {}
    for case in cases:
        for gap in case["gaps"]:
            ranked[gap] = ranked.get(gap, 0) + 1
    priorities = [{"gap": gap, "cases_blocked": count} for gap, count in sorted(ranked.items(), key=lambda item: (-item[1], item[0]))]
    return {
        "verified_at": REGISTRY["verified_at"],
        "cases": cases,
        "priorities": priorities,
        "source_backed_golden_cases": sum(1 for case in cases if case["source_snapshots_present"]),
        "total_golden_cases": len(cases),
        "master_proof_ready_for_demo": all(case["source_snapshots_present"] for case in cases),
        "production_ready": False,
        "built_since_first_audit": [
            "dated official-source snapshots for every golden case",
            "allowlisted live-fetch connector with SHA-256 receipts",
            "privacy-minimising hash-and-discard Evidence Vault contract",
            "freshness gate for stale rule-dependent tools",
            "initial source-backed rule-to-service dependency graph",
            "cross-repo capability composition graph"
        ],
        "reason": "All golden cases are source-backed and composition-ready for demonstration, but production still needs persistent secure infrastructure, current live-fetch execution, broader data connectors, domain validation and user testing."
    }
