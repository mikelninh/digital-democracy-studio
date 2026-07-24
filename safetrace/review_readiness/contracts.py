from __future__ import annotations

import argparse
import json
from pathlib import Path

from .model import DISCIPLINES, DISCLOSURE_DECISIONS, FINDING_STATUSES, SEVERITIES

SCHEMA_VERSION = "safetrace.review-readiness-contracts/1.8"


def document() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://mikelninh.github.io/digital-democracy-studio/safetrace/review_readiness/artifacts/review-readiness-contracts-1.8.json",
        "title": "SafeTrace Independent Review Readiness Contracts v1.8",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"const": SCHEMA_VERSION},
            "disciplines": {"type": "array", "items": {"type": "string", "enum": sorted(DISCIPLINES)}},
            "finding_severities": {"type": "array", "items": {"type": "string", "enum": sorted(SEVERITIES)}},
            "finding_statuses": {"type": "array", "items": {"type": "string", "enum": sorted(FINDING_STATUSES)}},
            "disclosure_decisions": {"type": "array", "items": {"type": "string", "enum": sorted(DISCLOSURE_DECISIONS)}},
            "review_slot": {
                "type": "object",
                "required": [
                    "discipline", "purpose", "minimum_qualification", "independent_required",
                    "external_reviewer_id", "conflict_declaration_id", "status",
                ],
            },
            "finding": {
                "type": "object",
                "required": [
                    "id", "discipline", "title", "severity", "status", "owner",
                    "remediation", "disclosure_decision", "opened_at", "synthetic_dry_run",
                ],
            },
            "study_protocol": {
                "type": "object",
                "required": [
                    "id", "study_type", "objective", "participant_requirements",
                    "consent_required", "collected_fields", "prohibited_fields", "metrics",
                    "stopping_rules", "status",
                ],
            },
            "readiness_decision": {
                "type": "object",
                "required": [
                    "status", "external_reviews_completed", "external_approvals",
                    "unresolved_critical_findings", "unresolved_high_findings",
                    "ready_to_invite_reviewers", "restricted_data_gate_open",
                    "partner_pilot_gate_open", "reasons",
                ],
            },
        },
        "required": [
            "schema_version", "disciplines", "finding_severities",
            "finding_statuses", "disclosure_decisions", "review_slot",
            "finding", "study_protocol", "readiness_decision",
        ],
    }


def serialised() -> str:
    return json.dumps(document(), ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    expected = document()
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(serialised(), encoding="utf-8")
    if args.check and json.loads(args.check.read_text(encoding="utf-8")) != expected:
        raise SystemExit("Committed review-readiness contracts differ from generated contracts")
    if not args.write and not args.check:
        print(json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
