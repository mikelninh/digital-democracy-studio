from __future__ import annotations

import argparse
import json
from pathlib import Path

from .vocabularies import ACTIONS, ROLES, SCHEMA_VERSION, VIEWS


def document() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://mikelninh.github.io/digital-democracy-studio/safetrace/investigation_desk/schemas/investigation-desk-contracts-1.6.json",
        "title": "SafeTrace Investigation Desk Contracts v1.6",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"const": SCHEMA_VERSION},
            "roles": {"type": "array", "items": {"type": "string", "enum": sorted(ROLES)}},
            "views": {"type": "array", "items": {"type": "string", "enum": sorted(VIEWS)}},
            "actions": {"type": "array", "items": {"type": "string", "enum": sorted(ACTIONS)}},
            "session": {
                "type": "object",
                "required": [
                    "subject_id", "role", "authenticated", "identity_provider",
                    "session_id", "data_zone_ceiling", "issued_at",
                ],
            },
            "audit_event": {
                "type": "object",
                "required": [
                    "id", "sequence", "case_id", "actor_id", "action",
                    "subject_id", "outcome", "occurred_at", "event_hash",
                ],
            },
            "public_export": {
                "type": "object",
                "required": [
                    "schema_version", "publication_id", "case_id", "exported_at",
                    "claims", "internal_comments_included", "internal_tasks_included",
                    "agent_proposals_included",
                ],
            },
        },
        "required": ["schema_version", "roles", "views", "actions", "session", "audit_event", "public_export"],
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
        raise SystemExit("Committed Investigation Desk contracts differ from generated contracts")
    if not args.write and not args.check:
        print(json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
