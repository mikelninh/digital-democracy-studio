from __future__ import annotations

import argparse
import json
from pathlib import Path


def document() -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://mikelninh.github.io/digital-democracy-studio/safetrace/case_004_reference/schemas/case-004-reference-contracts-1.7.json",
        "title": "SafeTrace Case 004 Reference Contracts v1.7",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "release_report": {
                "type": "object",
                "required": [
                    "schema_version", "status", "counts", "source_backfill",
                    "workflow", "benchmark", "comprehension", "artifacts", "boundaries",
                ],
            },
            "reference_pack": {
                "type": "object",
                "required": [
                    "schema_version", "edition", "case", "overall_verdict",
                    "overall_explanation", "publication_boundary", "measures",
                    "claims", "sources", "source_backfill", "workflow",
                    "benchmark", "comprehension", "monitoring", "limitations",
                ],
            },
            "comprehension_instrument": {
                "type": "object",
                "required": [
                    "schema_version", "questions", "concepts", "participant_count",
                    "observed_study_completed", "status",
                ],
            },
        },
        "required": ["release_report", "reference_pack", "comprehension_instrument"],
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
        raise SystemExit("Committed Case 004 reference contracts differ from generated contracts")
    if not args.write and not args.check:
        print(json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
