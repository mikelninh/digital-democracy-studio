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
    "core",
]


def _load_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "not_run", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "invalid", "path": str(path), "error": str(exc)}


def validate_repository(root: Path) -> dict[str, Any]:
    safetrace_root = root / "safetrace"
    missing = [name for name in REQUIRED_COMPONENTS if not (safetrace_root / name).exists()]

    governance_path = safetrace_root / "governance/data/readiness.json"
    pilot_path = safetrace_root / "pilot/data/synthetic_pilot.json"
    core_schema_path = safetrace_root / "core/schemas/safetrace-core-1.2.schema.json"
    migration_path = safetrace_root / "core/migration-report.json"

    controls, boundaries = load_governance(governance_path)
    synthetic_readiness = evaluate_readiness(controls, boundaries["synthetic_evaluation"])
    live_readiness = evaluate_readiness(controls, boundaries["restricted_partner"])
    pilot_evaluation = evaluate_pilot(load_pilot(pilot_path))
    migration_report = _load_optional_json(migration_path)

    core_schema_ready = core_schema_path.exists()
    migration_ready = (
        migration_report.get("status") == "pass"
        and migration_report.get("target_schema") == "safetrace.core/1.2"
        and set(migration_report.get("cases", {})) == {"case-001", "case-002", "case-003", "case-004"}
    )

    release_ready = (
        not missing
        and core_schema_ready
        and migration_ready
        and synthetic_readiness.ready
        and pilot_evaluation.decision == "GO_SYNTHETIC"
        and not live_readiness.ready
    )
    return {
        "schema_version": "safetrace.release-status/1.2",
        "release": "v1.2-unified-evidence-foundation",
        "release_ready": release_ready,
        "live_partner_ready": live_readiness.ready,
        "components": {name: name not in missing for name in REQUIRED_COMPONENTS},
        "core": {
            "schema_version": "safetrace.core/1.2",
            "schema_present": core_schema_ready,
            "migration": migration_report,
        },
        "synthetic_readiness": synthetic_readiness.to_dict(),
        "restricted_partner_readiness": live_readiness.to_dict(),
        "synthetic_pilot": pilot_evaluation.to_dict(),
        "truthful_status": (
            "SafeTrace v1.2 provides a unified, versioned evidence foundation and is ready for "
            "reviewed public records and synthetic evaluation. It is not authorised for real victim "
            "data or a restricted partner deployment."
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
