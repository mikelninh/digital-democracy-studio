from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from safetrace.governance.model import evaluate_readiness, load_governance
from safetrace.pilot.model import evaluate_pilot, load_pilot

REQUIRED_COMPONENTS = [
    "source_engine", "political_money", "review_desk", "arms_monitor",
    "monitoring", "case_packs", "governance", "pilot", "law_fairness",
    "core", "evidence_vault", "claim_ledger",
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

    controls, boundaries = load_governance(safetrace_root / "governance/data/readiness.json")
    synthetic_readiness = evaluate_readiness(controls, boundaries["synthetic_evaluation"])
    live_readiness = evaluate_readiness(controls, boundaries["restricted_partner"])
    pilot_evaluation = evaluate_pilot(load_pilot(safetrace_root / "pilot/data/synthetic_pilot.json"))

    core_schema_path = safetrace_root / "core/schemas/safetrace-core-1.2.schema.json"
    migration_report = _load_optional_json(safetrace_root / "core/migration-report.json")
    vault_contract_path = safetrace_root / "evidence_vault/schemas/evidence-vault-contracts-1.3.json"
    vault_report = _load_optional_json(safetrace_root / "evidence_vault/artifacts/release-report.json")
    ledger_contract_path = safetrace_root / "claim_ledger/artifacts/claim-ledger-contracts-1.4.json"
    ledger_report = _load_optional_json(safetrace_root / "claim_ledger/artifacts/release-report.json")

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
    ledger_fixture = ledger_report.get("synthetic_fixture", {})
    ledger_migration = ledger_report.get("existing_case_migration", {})
    ledger_ready = (
        ledger_contract_path.exists()
        and ledger_report.get("status") == "pass"
        and ledger_fixture.get("first_version_gate", {}).get("ready") is True
        and ledger_fixture.get("second_version_gate", {}).get("ready") is True
        and ledger_fixture.get("first_publication_status_after_correction") == "stale"
        and ledger_fixture.get("second_publication_status") == "published"
        and ledger_fixture.get("visible_correction") is True
        and ledger_migration.get("status") == "pass"
        and set(ledger_migration.get("cases", {})) == {"case-001", "case-002", "case-003", "case-004"}
        and ledger_migration.get("automatic_publications") == 0
    )

    release_ready = (
        not missing
        and core_schema_path.exists()
        and migration_ready
        and vault_ready
        and ledger_ready
        and synthetic_readiness.ready
        and pilot_evaluation.decision == "GO_SYNTHETIC"
        and not live_readiness.ready
    )
    return {
        "schema_version": "safetrace.release-status/1.4",
        "release": "v1.4-claim-ledger-2.0",
        "release_ready": release_ready,
        "live_partner_ready": live_readiness.ready,
        "components": {name: name not in missing for name in REQUIRED_COMPONENTS},
        "core": {"schema_version": "safetrace.core/1.2", "migration": migration_report},
        "evidence_vault": {"schema_version": "safetrace.evidence-vault/1.3", "release_evidence": vault_report},
        "claim_ledger": {"schema_version": "safetrace.claim-ledger/1.4", "release_evidence": ledger_report},
        "synthetic_readiness": synthetic_readiness.to_dict(),
        "restricted_partner_readiness": live_readiness.to_dict(),
        "synthetic_pilot": pilot_evaluation.to_dict(),
        "truthful_status": (
            "SafeTrace v1.4 provides a versioned, human-reviewed Claim Ledger for vault-backed public and synthetic evidence. "
            "Legacy claims are preserved but blocked for new publication until evidence backfill. Real victim and restricted partner data remain unauthorised."
        ),
    }


def write_release_status(root: Path, output: Path) -> dict[str, Any]:
    payload = validate_repository(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
