from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ALLOWED_STATES = {
    "implemented_self_verified",
    "documented_not_implemented",
    "pending_independent_review",
    "independently_verified",
    "partner_required",
}
EXTERNAL_ASSURANCE_TYPES = {"independent_security", "independent_legal", "data_protection", "qualified_partner"}
PASSING_STATES = {"implemented_self_verified", "independently_verified"}


def evaluate_readiness(config: dict[str, Any]) -> dict[str, Any]:
    controls = config["controls"]
    blockers: list[dict[str, str]] = []
    for control in controls:
        state = control["state"]
        if state not in ALLOWED_STATES:
            raise ValueError(f"Unsupported state for {control['id']}: {state}")
        if control.get("assurance_type") in EXTERNAL_ASSURANCE_TYPES and state == "implemented_self_verified":
            raise ValueError(f"External assurance control cannot be self-verified: {control['id']}")
        if control.get("required_for_pilot", True) and state not in PASSING_STATES:
            blockers.append({"id": control["id"], "title": control["title"], "state": state})

    sensitive_intake_enabled = bool(config["system_state"].get("sensitive_evidence_intake_enabled"))
    if sensitive_intake_enabled and blockers:
        raise ValueError("Sensitive evidence intake cannot be enabled while pilot blockers remain")

    counts = Counter(item["state"] for item in controls)
    pilot_ready = not blockers and config["system_state"].get("qualified_partner_named", False)
    return {
        "schema_version": "safetrace.readiness/0.9",
        "assessment_date": config["assessment_date"],
        "product_stage": "v1.0_controlled_pilot_ready" if pilot_ready else "v0.9_readiness_in_progress",
        "pilot_ready": pilot_ready,
        "sensitive_evidence_intake_enabled": sensitive_intake_enabled,
        "summary": dict(counts),
        "blockers": blockers,
        "controls": controls,
        "decision": (
            "GO: all required controls and qualified partner gate passed."
            if pilot_ready
            else "BLOCK: do not accept sensitive evidence or begin a real-world pilot."
        ),
    }


def build(config_path: Path, output_path: Path) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    report = evaluate_readiness(config)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path(__file__).parent / "controls.json")
    parser.add_argument("--output", type=Path, default=Path("artifacts/readiness/report.json"))
    args = parser.parse_args()
    build(args.config, args.output)


if __name__ == "__main__":
    main()
