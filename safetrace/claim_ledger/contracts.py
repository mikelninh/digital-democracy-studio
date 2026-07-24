from __future__ import annotations

import argparse
import json
from pathlib import Path

from safetrace.core.vocabularies import EVIDENCE_STATES, FIELD_SENSITIVITIES, LEGAL_STATUSES
from .vocabularies import *


def string(enum=None):
    schema = {"type": "string"}
    if enum is not None:
        schema["enum"] = sorted(enum)
    return schema


def nullable(schema):
    return {"anyOf": [schema, {"type": "null"}]}


def array(schema):
    return {"type": "array", "items": schema}


def obj(properties, required):
    return {"type": "object", "additionalProperties": False, "properties": properties, "required": required}


def document() -> dict:
    evidence = obj(
        {
            "id": string(), "claim_id": string(), "version": {"type": "integer", "minimum": 1},
            "role": string(EVIDENCE_ROLES), "provenance_mode": string(PROVENANCE_MODES),
            "source_id": string(), "anchor": string(), "summary": string(),
            "added_by": string(), "added_at": string(), "receipt_id": nullable(string()),
            "object_hash": nullable(string()), "legacy_url": nullable(string()),
        },
        ["id", "claim_id", "version", "role", "provenance_mode", "source_id", "anchor", "summary", "added_by", "added_at"],
    )
    version = obj(
        {
            "claim_id": string(), "version": {"type": "integer", "minimum": 1}, "text": string(),
            "evidence_state": string(EVIDENCE_STATES), "legal_status": string(LEGAL_STATUSES),
            "sensitivity": string(FIELD_SENSITIVITIES), "created_by": string(), "created_at": string(),
            "evidence_links": array({"$ref": "#/$defs/EvidenceLink"}), "limitations": array(string()),
            "metadata": {"type": "object"}, "supersedes_version": nullable({"type": "integer", "minimum": 1}),
        },
        ["claim_id", "version", "text", "evidence_state", "legal_status", "sensitivity", "created_by", "created_at", "evidence_links"],
    )
    claim = obj(
        {
            "id": string(), "case_id": string(), "researcher_id": string(), "material": {"type": "boolean"},
            "status": string(CLAIM_STATUSES), "current_version": {"type": "integer", "minimum": 1},
            "created_at": string(), "updated_at": string(),
            "versions": {"type": "object", "additionalProperties": {"$ref": "#/$defs/ClaimVersion"}},
        },
        ["id", "case_id", "researcher_id", "material", "status", "current_version", "created_at", "updated_at", "versions"],
    )
    task = obj(
        {
            "id": string(), "claim_id": string(), "version": {"type": "integer", "minimum": 1},
            "gate": string(REVIEW_GATES), "assignee_id": string(), "status": string(TASK_STATUSES),
            "created_at": string(), "required": {"type": "boolean"},
        },
        ["id", "claim_id", "version", "gate", "assignee_id", "status", "created_at"],
    )
    decision = obj(
        {
            "id": string(), "task_id": string(), "reviewer_id": string(),
            "outcome": string(TASK_STATUSES - {"pending"}), "rationale": string(),
            "decided_at": string(), "contradictory_evidence_addressed": {"type": "boolean"},
        },
        ["id", "task_id", "reviewer_id", "outcome", "rationale", "decided_at"],
    )
    publication = obj(
        {
            "id": string(), "case_id": string(),
            "claim_versions": array(array({"anyOf": [string(), {"type": "integer", "minimum": 1}]})),
            "status": string(PUBLICATION_STATUSES), "created_at": string(),
            "published_at": nullable(string()), "stale_reason": nullable(string()),
        },
        ["id", "case_id", "claim_versions", "status", "created_at"],
    )
    correction = obj(
        {
            "id": string(), "claim_id": string(), "from_version": {"type": "integer", "minimum": 1},
            "to_version": {"type": "integer", "minimum": 2}, "correction_type": string(CORRECTION_TYPES),
            "reason": string(), "approved_by": string(), "corrected_at": string(),
            "visible": {"type": "boolean"}, "invalidated_publication_ids": array(string()),
        },
        ["id", "claim_id", "from_version", "to_version", "correction_type", "reason", "approved_by", "corrected_at", "visible", "invalidated_publication_ids"],
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://mikelninh.github.io/digital-democracy-studio/safetrace/claim_ledger/schemas/claim-ledger-contracts-1.4.json",
        "title": "SafeTrace Claim Ledger Contracts v1.4",
        "$defs": {
            "EvidenceLink": evidence, "ClaimVersion": version, "LedgerClaim": claim,
            "ReviewTask": task, "ReviewDecision": decision,
            "LedgerPublication": publication, "LedgerCorrection": correction,
        },
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"const": SCHEMA_VERSION},
            "claims": array({"$ref": "#/$defs/LedgerClaim"}),
            "tasks": array({"$ref": "#/$defs/ReviewTask"}),
            "decisions": array({"$ref": "#/$defs/ReviewDecision"}),
            "publications": array({"$ref": "#/$defs/LedgerPublication"}),
            "corrections": array({"$ref": "#/$defs/LedgerCorrection"}),
        },
        "required": ["schema_version", "claims", "tasks", "decisions", "publications", "corrections"],
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
        raise SystemExit("Committed Claim Ledger contracts differ from generated contracts")
    if not args.write and not args.check:
        print(json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
