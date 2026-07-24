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
    "evidence_vault",
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
    vault_contract_path = safetrace_root / "evidence_vault/schemas/evidence-vault-contracts-1.3.json"
    vault_report_path = safetrace_root / "evidence_vault/artifacts/release-report.json"

    controls, boundaries = load_governance(governance_path)
    synthetic_readiness = evaluate_readiness(controls, boundaries["synthetic_evaluation"])
    live_readiness = evaluate_readiness(controls, boundaries["restricted_partner"])
    pilot_evaluation = evaluate_pilot(load_pilot(pilot_path))
    migration_report = _load_optional_json(migration_path)
    vault_report = _load_optional_json(vault_report_path)

    core_schema_ready = core_schema_path.exists()
    migration_ready = (
        migration_report.get("status") == "pass"
        and migration_report.get("target_schema") == "safetrace.core/1.2"
        and set(migration_report.get("cases", {})) == {"case-001", "case-002", "case-003", "case-004"}
    )
    vault_demo = vault_report.get("demo", {})
    vault_registry = vault_report.get("registry", {})
    vault_ready = (
        vault_contract_path.exists()
        and vault_report.get("status") == "pass"
        and vault_registry.get("status") == "pass"
        and vault_registry.get("sources", 0) >= vault_registry.get("minimum_expected_sources", 10)
        and vault_demo.get("receipt_chain_verified") is True
        and vault_demo.get("material_change_alert") == "material_change"
        and vault_demo.get("integrity", {}).get("status") == "pass"
        and vault_demo.get("restore_integrity", {}).get("status") == "pass"
    )

    release_ready = (
        not missing
        and core_schema_ready
        and migration_ready
        and vault_ready
        and synthetic_readiness.ready
        and pilot_evaluation.decision == "GO_SYNTHETIC"
        and not live_readiness.ready
    )
    return {
        "schema_version": "safetrace.release-status/1.3",
        "release": "v1.3-reviewed-source-registry-and-evidence-vault",
        "release_ready": release_ready,
        "live_partner_ready": live_readiness.ready,
        "components": {name: name not in missing for name in REQUIRED_COMPONENTS},
        "core": {
            "schema_version": "safetrace.core/1.2",
            "schema_present": core_schema_ready,
            "migration": migration_report,
        },
        "evidence_vault": {
            "schema_version": "safetrace.evidence-vault/1.3",
            "contracts_present": vault_contract_path.exists(),
            "release_evidence": vault_report,
        },
        "synthetic_readiness": synthetic_readiness.to_dict(),
        "restricted_partner_readiness": live_readiness.to_dict(),
        "synthetic_pilot": pilot_evaluation.to_dict(),
        "truthful_status": (
            "SafeTrace v1.3 provides a reviewed Source Registry and tamper-evident Evidence Vault "
            "for public sources and synthetic workflows. It is not authorised for real victim data "
            "or a restricted partner deployment."
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
