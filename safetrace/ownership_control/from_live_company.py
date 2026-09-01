from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .engine import run_case


def ownership_case_from_live_company(result: dict[str, Any]) -> dict[str, Any]:
    """Create a fail-closed ownership case from a live company investigation."""
    claims = {c["field"]: c for c in result.get("claims", [])}
    legal_name = claims.get("legal_name", {}).get("value") or result.get("case", {}).get("title", "Unresolved company")
    register_id = claims.get("register_id", {}).get("value")
    subject_id = str(register_id or legal_name).casefold().replace(" ", "-")

    sources = []
    for source in result.get("sources", []):
        if source.get("acquisition_status") == "acquired":
            sources.append({
                "id": source["id"],
                "title": source.get("title", source["id"]),
                "publisher": source.get("publisher"),
                "sha256": source.get("sha256"),
                "receipt_hash": source.get("receipt_hash"),
                "resolved_url": source.get("resolved_url"),
            })

    shareholder_gap = next(
        (
            gap for gap in result.get("unresolved_questions", [])
            if gap.get("field") == "shareholders"
            or "shareholder" in str(gap.get("title", "")).casefold()
            or "beneficial" in str(gap.get("title", "")).casefold()
        ),
        None,
    )
    reason = shareholder_gap.get("reason") if shareholder_gap else "The live company investigation did not establish a current shareholder list or ownership chain."

    return {
        "case_id": f"{result.get('case', {}).get('id', 'LIVE-COMPANY')}-OWNCTRL",
        "classification": "LIVE PUBLIC-SOURCE BOUNDARY",
        "target_entity_id": subject_id,
        "policy": {"ubo_threshold": 0.25, "ubo_threshold_operator": "gt", "control_rights_establish_candidate": True},
        "sources": sources,
        "entities": [{
            "id": subject_id,
            "name": legal_name,
            "kind": "company",
            "resolution_status": "confirmed" if claims.get("legal_name") else "unresolved",
            "identifiers": {"register_id": register_id} if register_id else {},
        }],
        "ownership_edges": [],
        "collection_gaps": [{
            "type": "shareholder_and_beneficial_ownership_not_established",
            "reason": reason,
            "status": "not_established",
            "next_step": shareholder_gap.get("next_step") if shareholder_gap else "Acquire the current authoritative shareholder list and preserve it as evidence before adding ownership edges.",
        }],
        "provenance": {
            "source_schema": result.get("schema_version"),
            "source_case_id": result.get("case", {}).get("id"),
            "source_receipts_preserved": [s["id"] for s in sources],
            "boundary": "No shareholder or UBO edge is inferred from company identity, management, website text, or missing evidence.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Turn a live company investigation into a fail-closed ownership/control boundary case.")
    parser.add_argument("--live-result", type=Path, required=True)
    parser.add_argument("--case-out", type=Path, required=True)
    parser.add_argument("--analysis-out", type=Path)
    args = parser.parse_args()

    live = json.loads(args.live_result.read_text(encoding="utf-8"))
    case = ownership_case_from_live_company(live)
    args.case_out.parent.mkdir(parents=True, exist_ok=True)
    args.case_out.write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.analysis_out:
        run_case(args.case_out, args.analysis_out)
    print(json.dumps({"case_id": case["case_id"], "ownership_edges": len(case["ownership_edges"]), "collection_gaps": len(case["collection_gaps"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
