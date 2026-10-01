from datetime import date
from pathlib import Path
import json

import engine
from change_impact import impact_plan
from claim_ledger import Claim, EvidenceReceipt, contradiction_pairs, explain_claim
from composition import compose_case, portfolio_graph
from connectors import SourceFetchError, _registered_source, connector_manifest
from evidence_vault import export_policy, ingest_bytes
from freshness_gate import gate_rule_dependent_tool
from golden_runner import run_all
from source_backing import build_gap_audit, source_pack

ROOT = Path(__file__).parent
ontology = json.loads((ROOT / "ontology.json").read_text(encoding="utf-8"))
golden = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))
registry = json.loads((ROOT / "source_registry.json").read_text(encoding="utf-8"))
snapshots = json.loads((ROOT / "source_snapshots.json").read_text(encoding="utf-8"))
modules = json.loads((ROOT / "module_contracts.json").read_text(encoding="utf-8"))["modules"]


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

        pack = source_pack(case["id"])
        check(pack["all_routes_verified"], f"{case['id']} needs authoritative source routes")
        check(pack["all_have_snapshots"], f"{case['id']} needs dated evidence snapshots")
        check(pack["source_count"] >= 1, f"{case['id']} must have at least one source")
        for source in pack["authoritative_sources"]:
            check(source["id"] in registry["sources"], f"unregistered source in {case['id']}")
            check(bool(source["snapshot_facts"]), f"source {source['id']} lacks snapshot facts")
            check(source["backing_state"] in {"verified_snapshot", "live_fetch"}, f"weak source state for {source['id']}")

        composition = compose_case(case["id"])
        check(composition["composition_ready"], f"{case['id']} has missing capability providers: {composition['missing_capabilities']}")
        check(composition["coverage"] == 1.0, f"{case['id']} must have full capability coverage")
        for binding in composition["bindings"]:
            if binding["status"] == "covered":
                provider = binding["selected_provider"]["module"]
                check(provider in modules, f"{case['id']} selected unknown module {provider}")

    sensitive_cases = [case for case in cases if case["expected"]["human_review"]]
    for case in sensitive_cases:
        plan = engine.build_plan(case["question"])
        check(plan["autonomous_action_allowed"] is False, f"{case['id']} crossed human approval boundary")
        check(plan["status"] == "source_backed_plan", f"{case['id']} should produce source-backed plan")
        check(bool(plan["next_best_action"]["why"]), f"{case['id']} needs next-action rationale")

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

    receipt = EvidenceReceipt(id="ev-1", source="synthetic://registry/a", source_type="registry", retrieved_at="2026-08-28T00:00:00+00:00")
    claim_a = Claim(id="claim-a", subject_id="org-1", predicate="DIRECTOR_OF", object_id="person-a", status="supported", evidence_ids=("ev-1",), valid_from="2026-01-01", confidence=0.9)
    claim_b = Claim(id="claim-b", subject_id="org-1", predicate="DIRECTOR_OF", object_id="person-b", status="unresolved", evidence_ids=("ev-2",), valid_from="2026-01-01", confidence=0.7)
    conflicts = contradiction_pairs([claim_a, claim_b])
    check(len(conflicts) == 1, "overlapping contradictory claims must be surfaced")
    check(conflicts[0]["review_state"] == "human_review_required", "contradiction must escalate")

    explained = explain_claim(claim_a, [receipt])
    check(len(explained["evidence"]) == 1, "claim must resolve its evidence receipt")
    check(not explained["missing_evidence_ids"], "supported proof fixture must have no missing receipt")

    manifest = connector_manifest()
    check(len(manifest) == len(registry["sources"]), "every registered source needs connector manifest entry")
    try:
        _registered_source("https://attacker.example/not-allowed")
    except SourceFetchError:
        pass
    else:
        raise AssertionError("connector must reject arbitrary/non-allowlisted source ids")

    private_receipt = ingest_bytes(b"synthetic personal document", media_type="text/plain", sensitivity="personal")
    check(private_receipt.raw_persisted is False, "master proof must default to no raw evidence persistence")
    check(private_receipt.sha256, "evidence intake must create integrity hash")
    private_export = export_policy(private_receipt)
    check(private_export["allowed"] is False, "personal evidence must not export automatically")
    check(private_export["requires_human_approval"] is True, "personal evidence export needs approval")

    stale_gate = gate_rule_dependent_tool(module="WohngeldMCP", data_as_of="2024-2025", today=date(2026, 8, 28))
    check(stale_gate.decision == "verify_first", "stale benefit parameters must fail closed into verification")
    current_gate = gate_rule_dependent_tool(module="synthetic-current", data_as_of="2026", today=date(2026, 8, 28))
    check(current_gate.decision == "allow", "current verified-year fixture should pass freshness gate")

    impact = impact_plan("BerlStrG:11", effective_date="2026-09-01")
    check(impact["status"] == "candidate_impact_found", "known rule dependency should produce candidate impact")
    check(impact["autonomous_case_change_allowed"] is False, "change impact may never auto-change case outcome")
    unknown_impact = impact_plan("UNKNOWN:RULE")
    check(unknown_impact["status"] == "dependency_unknown", "unknown dependency must fail bounded")

    report = run_all()
    check(report["passed"] == report["total"], "all source-backed golden experiences must pass contract")
    check(report["demo_readiness"] == "ready", "master proof must be demo-ready")
    check(report["production_readiness"] == "not_ready", "proof must not claim production readiness")

    portfolio = portfolio_graph()
    check(portfolio["cases_composition_ready"] == portfolio["total_cases"], "all golden cases need composable providers")
    check(portfolio["capability_coverage"] == 1.0, "all required capabilities need providers")

    audit = build_gap_audit()
    check(audit["source_backed_golden_cases"] == len(cases), "all golden cases need source snapshots")
    check(audit["production_ready"] is False, "gap audit must remain honest")
    check(any(item["gap"].startswith("execute allowlisted live fetch") for item in audit["priorities"]), "per-run live evidence gap must stay visible")
    check("freshness gate for stale rule-dependent tools" in audit["built_since_first_audit"], "freshness gate should be recorded as built")

    check(set(snapshots["snapshots"]) >= set(registry["sources"]), "every registered source needs a dated snapshot")

    print(f"PASS: {len(cases)} golden cases validated")
    print("PASS: ontology contract")
    print("PASS: authoritative source routes + dated evidence snapshots")
    print("PASS: human-approval boundaries")
    print("PASS: deterministic workflow probes")
    print("PASS: insufficient-grounding fallback")
    print("PASS: claim ledger evidence receipts + contradiction escalation")
    print("PASS: allowlisted source connector boundary")
    print("PASS: privacy-minimising evidence receipt + export gate")
    print("PASS: stale rule-dependent tools fail into verification")
    print("PASS: bounded rule-to-service change impact")
    print(f"PASS: source-backed end-to-end scorecard {report['passed']}/{report['total']}")
    print(f"PASS: cross-repo capability composition {portfolio['cases_composition_ready']}/{portfolio['total_cases']} cases, {portfolio['capability_coverage']:.0%} coverage")
    print("PASS: production gaps remain explicit")


if __name__ == "__main__":
    run()
