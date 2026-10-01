from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
GRAPH = json.loads((ROOT / "dependency_graph.json").read_text(encoding="utf-8"))


def impacted_services(rule_id: str) -> list[dict[str, Any]]:
    return [edge for edge in GRAPH["edges"] if edge["rule_id"] == rule_id]


def impact_plan(rule_id: str, *, effective_date: str | None = None) -> dict[str, Any]:
    edges = impacted_services(rule_id)
    if not edges:
        return {
            "rule_id": rule_id,
            "status": "dependency_unknown",
            "affected_services": [],
            "candidate_cases": [],
            "human_review_required": True,
            "next_action": "Map the rule to services using authoritative evidence before filtering cases.",
            "autonomous_case_change_allowed": False,
        }

    service_ids = {edge["service_id"] for edge in edges}
    cases = [link for link in GRAPH["synthetic_case_links"] if link["service_id"] in service_ids]
    return {
        "rule_id": rule_id,
        "status": "candidate_impact_found",
        "effective_date": effective_date,
        "affected_services": edges,
        "candidate_cases": cases,
        "human_review_required": True,
        "next_action": "Verify the promulgated change/effective date, diff the provision, then review candidate workflows/cases in priority order.",
        "autonomous_case_change_allowed": False,
        "boundary": "A dependency edge identifies where review may be needed; it does not prove a case outcome changes."
    }
