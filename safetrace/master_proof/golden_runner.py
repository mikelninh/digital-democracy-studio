from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import engine
from source_backing import build_gap_audit, source_pack

ROOT = Path(__file__).parent
GOLDEN = json.loads((ROOT / "golden_cases.json").read_text(encoding="utf-8"))
EXPERIENCES = json.loads((ROOT / "golden_experiences.json").read_text(encoding="utf-8"))["experiences"]


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    case_id = case["id"]
    experience = EXPERIENCES[case_id]
    plan = engine.build_plan(case["question"])
    sources = source_pack(case_id)
    checks = {
        "workflow_matched": plan.get("matched_case") == case_id,
        "authoritative_routes": sources["all_routes_verified"],
        "dated_source_snapshots": sources["all_have_snapshots"],
        "next_action_present": bool(plan.get("next_best_action", {}).get("label")),
        "why_present": bool(plan.get("why", {}).get("authoritative_sources")),
        "uncertainty_visible": bool(plan.get("uncertainty")),
        "negative_boundaries": bool(plan.get("must_not")),
        "approval_boundary": (not case["expected"]["human_review"]) or plan.get("autonomous_action_allowed") is False,
        "success_conditions_defined": bool(experience["success_conditions"])
    }
    passed = all(checks.values())
    return {
        "case_id": case_id,
        "title": experience["title"],
        "persona": case["persona"],
        "domain": case["domain"],
        "sample_inputs": experience["sample_inputs"],
        "status": "pass" if passed else "fail",
        "checks": checks,
        "next_best_action": plan.get("next_best_action"),
        "source_count": sources["source_count"],
        "source_states": sorted({source["backing_state"] for source in sources["authoritative_sources"]}),
        "success_conditions": experience["success_conditions"],
        "must_not": case["must_not"]
    }


def run_all() -> dict[str, Any]:
    results = [run_case(case) for case in GOLDEN["cases"]]
    audit = build_gap_audit()
    passed = sum(1 for result in results if result["status"] == "pass")
    return {
        "suite": "CivicOS source-backed golden experiences",
        "version": EXPERIENCES and "0.2.0",
        "passed": passed,
        "total": len(results),
        "pass_rate": round(passed / len(results), 4) if results else 0,
        "demo_readiness": "ready" if passed == len(results) and audit["master_proof_ready_for_demo"] else "not_ready",
        "production_readiness": "not_ready" if not audit["production_ready"] else "ready",
        "results": results,
        "top_gaps": audit["priorities"]
    }


def markdown_scorecard(report: dict[str, Any]) -> str:
    lines = [
        "# CivicOS Golden Experience Scorecard",
        "",
        f"**Contract pass:** {report['passed']}/{report['total']} ({report['pass_rate']:.0%})",
        f"**Demo readiness:** {report['demo_readiness']}",
        f"**Production readiness:** {report['production_readiness']}",
        "",
        "| Golden case | Domain | Sources | Status |",
        "|---|---|---:|---|"
    ]
    for result in report["results"]:
        lines.append(f"| {result['title']} | {result['domain']} | {result['source_count']} | {result['status'].upper()} |")
    lines.extend(["", "## Remaining gaps"])
    for item in report["top_gaps"]:
        lines.append(f"- **{item['gap']}** — affects {item['cases_blocked']} case(s)")
    lines.extend([
        "",
        "> Passing means the source/evidence/action contract is present and regression-tested. It does not mean a case-specific legal, eligibility, fraud or administrative conclusion has been validated for a real person or organisation."
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    report = run_all()
    print(markdown_scorecard(report))
