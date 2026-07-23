from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from safetrace.governance.model import evaluate_readiness, load_governance
from safetrace.pilot.model import evaluate_pilot, load_pilot

REQUIRED_COMPONENTS = [
    "source_engine",
    "political_money",
    "review_desk",
    "arms_monitor",
    "monitoring",
    "case_packs",
    "governance",
    "pilot",
    "law_fairness",
]


def validate_repository(root: Path) -> dict[str, Any]:
    safetrace_root = root / "safetrace"
    missing = [name for name in REQUIRED_COMPONENTS if not (safetrace_root / name).exists()]

    governance_path = safetrace_root / "governance/data/readiness.json"
    pilot_path = safetrace_root / "pilot/data/synthetic_pilot.json"
    controls, boundaries = load_governance(governance_path)
    synthetic_readiness = evaluate_readiness(controls, boundaries["synthetic_evaluation"])
    live_readiness = evaluate_readiness(controls, boundaries["restricted_partner"])
    pilot_evaluation = evaluate_pilot(load_pilot(pilot_path))

    release_ready = (
        not missing
        and synthetic_readiness.ready
        and pilot_evaluation.decision == "GO_SYNTHETIC"
        and not live_readiness.ready
    )
    return {
        "schema_version": "safetrace.release-status/1.0",
        "release": "v1.0-pilot-ready",
        "release_ready": release_ready,
        "live_partner_ready": live_readiness.ready,
        "components": {name: name not in missing for name in REQUIRED_COMPONENTS},
        "synthetic_readiness": synthetic_readiness.to_dict(),
        "restricted_partner_readiness": live_readiness.to_dict(),
        "synthetic_pilot": pilot_evaluation.to_dict(),
        "truthful_status": (
            "SafeTrace v1.0 is pilot-ready for public and synthetic evaluation. "
            "It is not authorised for real victim data or a restricted partner deployment."
        ),
    }


def write_release_status(root: Path, output: Path) -> dict[str, Any]:
    payload = validate_repository(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload
