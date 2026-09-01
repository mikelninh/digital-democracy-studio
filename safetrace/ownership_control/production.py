from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import engine
from .workspace import render_html as render_workspace_html


def _target_identity_gap(data: dict[str, Any]) -> dict[str, Any] | None:
    entities = {item.get("id"): item for item in data.get("entities", [])}
    target_id = data.get("target_entity_id")
    target = entities.get(target_id)
    if target is None:
        return {
            "type": "target_identity_not_established",
            "status": "blocked",
            "reason": "The target entity is missing from the entity set. Ownership/control propagation cannot start.",
        }
    resolution = target.get("resolution_status", "unresolved")
    if resolution != "confirmed":
        return {
            "type": "target_identity_not_established",
            "status": f"blocked_identity_{resolution}",
            "entity_id": target_id,
            "entity_name": target.get("name", target_id),
            "reason": "Ownership/control propagation requires a confirmed target identity before any relationship is treated as belonging to the subject.",
        }
    return None


def _empty_fail_closed_result(data: dict[str, Any], gap: dict[str, Any]) -> dict[str, Any]:
    entities = {item.get("id"): item for item in data.get("entities", [])}
    target_id = data.get("target_entity_id")
    target = entities.get(target_id, {})
    return {
        "schema_version": "safetrace.ownership-control/1.1",
        "case_id": data.get("case_id", "UNKNOWN"),
        "classification": data.get("classification", "unspecified"),
        "subject": {
            "id": target_id,
            "name": target.get("name", "Unresolved target"),
            "kind": target.get("kind", "other"),
            "resolution_status": target.get("resolution_status", "unresolved"),
        },
        "policy": data.get("policy", {}),
        "economic_ownership": [],
        "voting_rights": [],
        "control_signals": [],
        "ubo_candidates": [],
        "screening_handoff": [],
        "unresolved": [gap],
        "source_ids_used": [],
        "metrics": {
            "entities": len(data.get("entities", [])),
            "ownership_edges": len(data.get("ownership_edges", [])),
            "established_edges": 0,
            "economic_paths": 0,
            "voting_paths": 0,
            "control_signals": 0,
            "ubo_candidates": 0,
            "screening_handoff": 0,
            "cycles": 0,
            "blocked_paths": 0,
            "unresolved_items": 1,
        },
        "decision_boundary": {
            "ownership_established": False,
            "voting_control_established": False,
            "beneficial_ownership_complete": False,
            "human_review_required": True,
            "statement": "Target identity is not confirmed, so ownership/control propagation is blocked before graph analysis.",
        },
        "guardrails": [
            "No ownership/control conclusion is generated for an unresolved target identity.",
            "No screening handoff is generated from an unresolved target identity.",
            "Human review is required before consequential use.",
        ],
    }


def _screening_handoff(result: dict[str, Any], data: dict[str, Any]) -> list[dict[str, Any]]:
    entities = {item["id"]: item for item in data.get("entities", [])}
    handoff: list[dict[str, Any]] = []
    for candidate in result.get("ubo_candidates", []):
        entity = entities.get(candidate["entity_id"], {})
        if entity.get("kind") != "person" or entity.get("resolution_status") != "confirmed":
            continue
        handoff.append({
            "entity_id": candidate["entity_id"],
            "name": candidate["name"],
            "identity_status": "confirmed",
            "identifiers": entity.get("identifiers", {}),
            "handoff_status": "ready_for_authoritative_screening",
            "reason": "Natural-person candidate under the configured ownership/control rule; screen against authoritative lists at decision time.",
            "candidate_grounds": candidate.get("grounds", []),
            "boundary": "Screening handoff is a research lead. It is not a sanctions match and does not convert a rule-scoped UBO candidate into a final legal UBO determination.",
        })
    return sorted(handoff, key=lambda item: (item["name"], item["entity_id"]))


def investigate(data: dict[str, Any]) -> dict[str, Any]:
    gap = _target_identity_gap(data)
    if gap:
        return _empty_fail_closed_result(data, gap)

    result = engine.investigate(data)
    result = {**result, "schema_version": "safetrace.ownership-control/1.1"}
    handoff = _screening_handoff(result, data)
    result["screening_handoff"] = handoff
    result["metrics"] = {**result["metrics"], "screening_handoff": len(handoff)}
    result["decision_boundary"] = {
        **result["decision_boundary"],
        "screening_statement": "Only confirmed natural-person rule candidates are handed to a separate authoritative screening stage. No sanctions conclusion is made here.",
    }
    result["guardrails"] = [
        *result.get("guardrails", []),
        "Target identity must be confirmed before production graph propagation.",
        "Screening is a separate stage; a handoff record is not a sanctions match.",
    ]
    return result


def run_case(case_path: Path, out_dir: Path) -> dict[str, Any]:
    data = json.loads(case_path.read_text(encoding="utf-8"))
    result = investigate(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out_dir / "report.md").write_text(engine.render_markdown(result), encoding="utf-8")
    (out_dir / "index.html").write_text(render_workspace_html(result, data), encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run fail-closed production ownership/control analysis.")
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("artifacts/ownership-control"))
    args = parser.parse_args()
    result = run_case(args.case, args.out)
    print(json.dumps(result["metrics"], indent=2))
    print(f"Screening handoff: {[item['name'] for item in result['screening_handoff']]}")
    if any(row.get("integrity_warning") for row in result.get("economic_ownership", [])):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
