from __future__ import annotations

import argparse
import json
from pathlib import Path

from .vocabularies import SCHEMA_VERSION
from .workers import PROFILES


def document() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://mikelninh.github.io/digital-democracy-studio/safetrace/agent_queue/schemas/agent-queue-contracts-1.5.json",
        "title": "SafeTrace Auditable Agent Queue v1.5",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "schema_version": {"const": SCHEMA_VERSION},
            "agent_types": {
                "type": "array",
                "items": {"type": "string", "enum": sorted(PROFILES)},
            },
            "task": {
                "type": "object",
                "required": [
                    "id", "case_id", "purpose", "agent_type", "allowed_tools",
                    "max_data_zone", "input_schema", "output_schema", "model_id",
                    "prompt_version", "timeout_seconds", "budget_cents",
                    "human_approver", "input_refs", "created_at",
                ],
            },
            "run_receipt": {
                "type": "object",
                "required": [
                    "run_id", "task_id", "model_id", "prompt_version",
                    "input_hash", "output_hash", "tool_calls", "cost_cents",
                    "latency_ms", "started_at", "completed_at", "trace_key",
                ],
            },
            "proposal": {
                "type": "object",
                "required": [
                    "id", "task_id", "run_id", "agent_type", "status",
                    "output", "anchors", "created_at",
                ],
            },
        },
        "required": ["schema_version", "agent_types", "task", "run_receipt", "proposal"],
    }


def serialised() -> str:
    return json.dumps(
        document(), ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ) + "\n"


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
        raise SystemExit("Committed Agent Queue contracts differ from generated contracts")
    if not args.write and not args.check:
        print(json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
