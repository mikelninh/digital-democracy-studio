"""Cross-case SafeTrace audit for v1.0 readiness.

The audit evaluates every opened case and discovery candidate without changing
its truth status. It checks whether priority, action, fairness, publication and
impact measurement are operationally specified.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAFE_ROOT = ROOT.parent
ANIMAL_CASES = SAFE_ROOT / "animal_welfare_series" / "cases.json"
CANDIDATES = ROOT / "candidates.json"
SOCIAL = ROOT / "social_seasons.json"
OUTPUT = ROOT / "v1_audit_report.json"

ACTION_VERBS = (
    "anfrag", "vergleich", "erfass", "kartier", "bau", "prüf", "test",
    "verfolg", "auswert", "überwach", "stell", "simulier", "verbinde",
)
DELIVERABLE_WORDS = (
    "matrix", "tracker", "dashboard", "datensatz", "statistik", "anfrage",
    "bericht", "register", "simulation", "scoreboard", "übersicht", "map",
)


def load_records() -> list[dict[str, object]]:
    animal = json.loads(ANIMAL_CASES.read_text(encoding="utf-8"))["cases"]
    discovery = json.loads(CANDIDATES.read_text(encoding="utf-8"))["candidates"]
    seasons = json.loads(SOCIAL.read_text(encoding="utf-8"))["seasons"]
    social = [candidate for season in seasons for candidate in season["candidates"]]

    records: list[dict[str, object]] = []
    for item in animal:
        records.append({"kind": "opened_case", "season": "Tierwohl", **item})
    for item in discovery:
        records.append({"kind": "candidate", "season": "Tierwohl-Radar", **item})
    for season in seasons:
        for item in season["candidates"]:
            records.append({"kind": "candidate", "season": season["title"], **item})
    return records


def priority_total(item: dict[str, object]) -> int:
    if item["kind"] == "opened_case":
        return int(item["priority"]["total"])
    return int(item["total"])


def action_text(item: dict[str, object]) -> str:
    return str(item.get("next_action") or item.get("first_sprint") or "")


def action_clarity(item: dict[str, object]) -> dict[str, object]:
    text = action_text(item).lower()
    score = 0
    if text:
        score += 1
    if any(word in text for word in ACTION_VERBS):
        score += 1
    if any(word in text for word in DELIVERABLE_WORDS):
        score += 1
    if item.get("action_owner"):
        score += 1
    if item.get("action_deadline") and item.get("stop_condition"):
        score += 1
    return {
        "score": score,
        "has_action": bool(text),
        "has_owner": bool(item.get("action_owner")),
        "has_deadline_and_stop_condition": bool(item.get("action_deadline") and item.get("stop_condition")),
    }


def impact_readiness(item: dict[str, object]) -> dict[str, object]:
    metrics = item.get("impact_metrics") or []
    conceptually_measurable = bool(metrics)
    required = (
        "impact_baseline", "impact_target", "impact_data_source",
        "impact_owner", "impact_cadence",
    )
    complete = all(item.get(field) for field in required)
    return {
        "metrics_list_present": conceptually_measurable,
        "operational_contract_complete": complete,
        "missing_fields": [field for field in required if not item.get(field)],
    }


def fairness_readiness(item: dict[str, object]) -> dict[str, object]:
    return {
        "explicit_unknowns": bool(item.get("not_established")),
        "win_win_path": bool(item.get("win_win_win")),
        "review_status": bool(item.get("review_status")),
        "right_of_reply_status": bool((item.get("review_status") or {}).get("right_of_reply")) if isinstance(item.get("review_status"), dict) else False,
    }


def publication_readiness(item: dict[str, object]) -> dict[str, object]:
    return {
        "state_defined": bool(item.get("publication_readiness")),
        "verdict_defined": bool(item.get("verdict")),
        "verified_claims_defined": bool(item.get("verified_claims")),
    }


def audit() -> dict[str, object]:
    records = load_records()
    audited = []
    for item in records:
        audited.append({
            "id": item["id"],
            "kind": item["kind"],
            "season": item["season"],
            "title": item.get("story_title") or item.get("title"),
            "priority": priority_total(item),
            "sources": len(item.get("sources") or []),
            "action": action_clarity(item),
            "impact": impact_readiness(item),
            "fairness": fairness_readiness(item),
            "publication": publication_readiness(item),
        })

    totals = len(audited)
    opened = [x for x in audited if x["kind"] == "opened_case"]
    candidates = [x for x in audited if x["kind"] == "candidate"]
    priority_distribution = Counter(x["priority"] for x in audited)
    season_distribution = Counter(x["season"] for x in audited)

    findings = {
        "all_have_source": all(x["sources"] >= 1 for x in audited),
        "single_source_records": sum(x["sources"] == 1 for x in audited),
        "high_priority_24_plus": sum(x["priority"] >= 24 for x in audited),
        "very_high_priority_29_plus": sum(x["priority"] >= 29 for x in audited),
        "action_text_present": sum(x["action"]["has_action"] for x in audited),
        "action_owner_present": sum(x["action"]["has_owner"] for x in audited),
        "deadline_and_stop_condition_present": sum(x["action"]["has_deadline_and_stop_condition"] for x in audited),
        "impact_metrics_list_present": sum(x["impact"]["metrics_list_present"] for x in audited),
        "operational_impact_contract_complete": sum(x["impact"]["operational_contract_complete"] for x in audited),
        "explicit_unknowns_present": sum(x["fairness"]["explicit_unknowns"] for x in audited),
        "win_win_path_present": sum(x["fairness"]["win_win_path"] for x in audited),
        "publication_state_defined": sum(x["publication"]["state_defined"] for x in audited),
    }

    conclusions = [
        "Priority is strongly compressed: a high score does not yet create a usable work queue.",
        "Every record has a next research instruction, but ownership, deadline and stop conditions are not operationalised.",
        "Opened cases list possible impact metrics, yet no case has a complete baseline-target-source-owner-cadence contract.",
        "Fairness and publication fields are mature in opened cases but mostly absent from discovery candidates.",
        "v1.0 must separate public importance, investigation feasibility, publication readiness and impact readiness.",
    ]

    return {
        "schema": "safetrace.v1-readiness-audit/0.1",
        "generated_at": "2026-07-26",
        "total_records": totals,
        "opened_cases": len(opened),
        "discovery_candidates": len(candidates),
        "season_distribution": dict(sorted(season_distribution.items())),
        "priority_distribution": {str(k): v for k, v in sorted(priority_distribution.items(), reverse=True)},
        "findings": findings,
        "conclusions": conclusions,
        "records": audited,
    }


def main() -> int:
    report = audit()
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("schema", "total_records", "opened_cases", "discovery_candidates", "findings")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
