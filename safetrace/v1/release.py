from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from safetrace.governance.model import evaluate_readiness, load_governance
from safetrace.pilot.model import evaluate_pilot, load_pilot

REQUIRED_COMPONENTS = [
    "source_engine", "political_money", "review_desk", "arms_monitor",
    "monitoring", "case_packs", "governance", "pilot", "law_fairness",
    "core", "evidence_vault", "claim_ledger", "agent_queue", "investigation_desk",
    "case_004_reference",
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
    agent_contract_path = safetrace_root / "agent_queue/artifacts/agent-queue-contracts-1.5.json"
    agent_report = _load_optional_json(safetrace_root / "agent_queue/artifacts/release-report.json")
    desk_contract_path = safetrace_root / "investigation_desk/artifacts/investigation-desk-contracts-1.6.json"
    desk_report = _load_optional_json(safetrace_root / "investigation_desk/artifacts/release-report.json")
    reference_contract_path = safetrace_root / "case_004_reference/artifacts/case-004-reference-contracts-1.7.json"
    reference_report = _load_optional_json(safetrace_root / "case_004_reference/artifacts/release-report.json")
    reference_json_path = safetrace_root / "case_004_reference/artifacts/case-004-reference-pack.json"
    reference_pdf_path = safetrace_root / "case_004_reference/artifacts/case-004-reference-pack.pdf"
    comprehension_path = safetrace_root / "case_004_reference/artifacts/comprehension-instrument.json"
    monitoring_path = safetrace_root / "case_004_reference/artifacts/monitoring-manifest.json"

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
    agent_workers = agent_report.get("workers", {})
    agent_metrics = agent_report.get("metrics", {})
    agent_evaluation = agent_report.get("evaluation", {})
    agent_boundaries = agent_report.get("boundaries", {})
    agent_ready = (
        agent_contract_path.exists()
        and agent_report.get("status") == "pass"
        and agent_workers.get("count") == 12
        and len(agent_workers.get("implemented", [])) == 12
        and agent_metrics.get("auto_approved") == 0
        and agent_metrics.get("awaiting_human") == 12
        and agent_metrics.get("receipts") == 12
        and agent_evaluation.get("status") == "pass"
        and agent_evaluation.get("passed") == agent_evaluation.get("total")
        and agent_evaluation.get("unsafe_accepted") == 0
        and agent_boundaries.get("proposal_only") is True
        and agent_boundaries.get("autonomous_publication") is False
        and agent_boundaries.get("autonomous_contact") is False
        and agent_boundaries.get("autonomous_referral") is False
        and agent_boundaries.get("restricted_partner_data") is False
    )
    desk_views = desk_report.get("views", {})
    desk_roles = desk_report.get("roles", {})
    desk_workflow = desk_report.get("workflow", {})
    desk_export = desk_workflow.get("public_export", {})
    desk_audit = desk_report.get("audit", {})
    desk_boundaries = desk_report.get("boundaries", {})
    desk_prohibited = desk_report.get("prohibited_actions", {})
    desk_ready = (
        desk_contract_path.exists()
        and desk_report.get("status") == "pass"
        and desk_views.get("count") == 11
        and len(desk_views.get("implemented", [])) == 11
        and desk_roles.get("synthetic_authenticated_sessions") is True
        and desk_roles.get("production_identity_provider_configured") is False
        and desk_workflow.get("claim_review_state") == "approved"
        and desk_workflow.get("agent_proposal_status") == "accepted_for_review"
        and desk_workflow.get("publication_status_after_correction") == "stale"
        and desk_export.get("internal_comments_included") is False
        and desk_export.get("internal_tasks_included") is False
        and desk_export.get("agent_proposals_included") is False
        and desk_audit.get("status") == "pass"
        and desk_audit.get("events", 0) >= 10
        and "cannot perform approve_publication" in desk_prohibited.get("investigator_publish_approval", "")
        and "Authenticated internal session required" in desk_prohibited.get("unauthenticated_action", "")
        and desk_boundaries.get("authoritative_internal_system") is True
        and desk_boundaries.get("public_portal_separate") is True
        and desk_boundaries.get("agent_proposals_auto_publish") is False
        and desk_boundaries.get("production_auth_ready") is False
        and desk_boundaries.get("restricted_partner_data") is False
    )
    reference_counts = reference_report.get("counts", {})
    reference_backfill = reference_report.get("source_backfill", {})
    reference_workflow = reference_report.get("workflow", {})
    reference_audit = reference_workflow.get("audit", {})
    reference_benchmark = reference_report.get("benchmark", {})
    reference_comprehension = reference_report.get("comprehension", {})
    reference_boundaries = reference_report.get("boundaries", {})
    reference_ready = (
        reference_contract_path.exists()
        and reference_json_path.exists()
        and reference_pdf_path.exists()
        and comprehension_path.exists()
        and monitoring_path.exists()
        and reference_report.get("status") == "pass"
        and reference_counts.get("sources") == 11
        and reference_counts.get("measures") == 5
        and reference_counts.get("claims") == 5
        and reference_counts.get("agent_proposals") == 4
        and reference_counts.get("desk_views") == 11
        and reference_backfill.get("sources_registered") == 11
        and reference_backfill.get("original_bytes_backfilled") == 0
        and reference_backfill.get("publication_allowed") is False
        and reference_workflow.get("human_reviewed_claims") == 5
        and reference_workflow.get("agent_proposals_accepted_for_review") == 4
        and reference_workflow.get("publication_requests") == 0
        and reference_audit.get("status") == "pass"
        and reference_benchmark.get("target_met_in_fixture") is True
        and reference_benchmark.get("observed_human_time_measurement") is False
        and reference_benchmark.get("real_partner_impact_claimed") is False
        and reference_comprehension.get("participant_count") == 0
        and reference_comprehension.get("observed_study_completed") is False
        and len(reference_comprehension.get("concepts", [])) >= 4
        and reference_boundaries.get("technical_reference_complete") is True
        and reference_boundaries.get("new_publication_allowed") is False
        and reference_boundaries.get("real_partner_impact_claimed") is False
        and reference_boundaries.get("external_comprehension_study_completed") is False
        and reference_boundaries.get("restricted_partner_data") is False
    )

    release_ready = (
        not missing
        and core_schema_path.exists()
        and migration_ready
        and vault_ready
        and ledger_ready
        and agent_ready
        and desk_ready
        and reference_ready
        and synthetic_readiness.ready
        and pilot_evaluation.decision == "GO_SYNTHETIC"
        and not live_readiness.ready
    )
    return {
        "schema_version": "safetrace.release-status/1.7",
        "release": "v1.7-case-004-technical-reference",
        "release_ready": release_ready,
        "live_partner_ready": live_readiness.ready,
        "components": {name: name not in missing for name in REQUIRED_COMPONENTS},
        "core": {"schema_version": "safetrace.core/1.2", "migration": migration_report},
        "evidence_vault": {"schema_version": "safetrace.evidence-vault/1.3", "release_evidence": vault_report},
        "claim_ledger": {"schema_version": "safetrace.claim-ledger/1.4", "release_evidence": ledger_report},
        "agent_queue": {"schema_version": "safetrace.agent-queue/1.5", "release_evidence": agent_report},
        "investigation_desk": {"schema_version": "safetrace.investigation-desk/1.6", "release_evidence": desk_report},
        "case_004_reference": {"schema_version": "safetrace.case004-reference/1.7", "release_evidence": reference_report},
        "synthetic_readiness": synthetic_readiness.to_dict(),
        "restricted_partner_readiness": live_readiness.to_dict(),
        "synthetic_pilot": pilot_evaluation.to_dict(),
        "truthful_status": (
            "SafeTrace v1.7 completes the deterministic Case 004 technical reference workflow with reviewed repository records, "
            "Desk views, agent proposals, audit, JSON/PDF, monitoring, benchmark and comprehension instruments. A newly verified "
            "public publication remains blocked because original source bytes are not yet backfilled; real time savings and citizen "
            "comprehension remain unmeasured external outcomes."
        ),
    }


def write_release_status(root: Path, output: Path) -> dict[str, Any]:
    payload = validate_repository(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
