from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from safetrace.v1.release import validate_repository, write_release_status


class ReleaseTests(unittest.TestCase):
    def _make_repository(self, root: Path) -> None:
        source_root = Path(__file__).parents[2]
        components = [
            "source_engine", "political_money", "review_desk", "arms_monitor",
            "monitoring", "case_packs", "governance", "pilot", "law_fairness",
            "core", "evidence_vault", "claim_ledger", "agent_queue",
            "investigation_desk", "case_004_reference", "review_readiness",
        ]
        for component in components:
            (root / "safetrace" / component).mkdir(parents=True, exist_ok=True)
        for path in (
            "governance/data", "pilot/data", "core/schemas", "evidence_vault/schemas",
            "evidence_vault/artifacts", "claim_ledger/artifacts", "agent_queue/artifacts",
            "investigation_desk/artifacts", "case_004_reference/artifacts",
            "review_readiness/artifacts",
        ):
            (root / "safetrace" / path).mkdir(parents=True, exist_ok=True)

        (root / "safetrace/governance/data/readiness.json").write_text(
            (source_root / "governance/data/readiness.json").read_text(encoding="utf-8"), encoding="utf-8"
        )
        (root / "safetrace/pilot/data/synthetic_pilot.json").write_text(
            (source_root / "pilot/data/synthetic_pilot.json").read_text(encoding="utf-8"), encoding="utf-8"
        )
        required_files = (
            "core/schemas/safetrace-core-1.2.schema.json",
            "evidence_vault/schemas/evidence-vault-contracts-1.3.json",
            "claim_ledger/artifacts/claim-ledger-contracts-1.4.json",
            "agent_queue/artifacts/agent-queue-contracts-1.5.json",
            "investigation_desk/artifacts/investigation-desk-contracts-1.6.json",
            "case_004_reference/artifacts/case-004-reference-contracts-1.7.json",
            "case_004_reference/artifacts/case-004-reference-pack.json",
            "case_004_reference/artifacts/case-004-reference-pack.pdf",
            "case_004_reference/artifacts/comprehension-instrument.json",
            "case_004_reference/artifacts/monitoring-manifest.json",
            "review_readiness/artifacts/review-readiness-contracts-1.8.json",
            "review_readiness/artifacts/review-readiness-dossier.pdf",
            "review_readiness/artifacts/finding-register.json",
            "review_readiness/artifacts/source-backfill-plan.json",
            "review_readiness/artifacts/study-protocols.json",
            "review_readiness/artifacts/review-packets.json",
        )
        for path in required_files:
            (root / "safetrace" / path).write_bytes(b"{}" if not path.endswith(".pdf") else b"%PDF-fixture")

        (root / "safetrace/core/migration-report.json").write_text(json.dumps({
            "status": "pass", "target_schema": "safetrace.core/1.2",
            "cases": {case_id: {} for case_id in ("case-001", "case-002", "case-003", "case-004")},
        }), encoding="utf-8")
        (root / "safetrace/evidence_vault/artifacts/release-report.json").write_text(json.dumps({
            "status": "pass",
            "registry": {"status": "pass", "sources": 20, "minimum_expected_sources": 10},
            "demo": {
                "receipt_chain_verified": True, "material_change_alert": "material_change",
                "integrity": {"status": "pass"}, "restore_integrity": {"status": "pass"},
            },
        }), encoding="utf-8")
        (root / "safetrace/claim_ledger/artifacts/release-report.json").write_text(json.dumps({
            "status": "pass",
            "synthetic_fixture": {
                "first_version_gate": {"ready": True}, "second_version_gate": {"ready": True},
                "first_publication_status_after_correction": "stale",
                "second_publication_status": "published", "visible_correction": True,
            },
            "existing_case_migration": {
                "status": "pass",
                "cases": {case_id: {} for case_id in ("case-001", "case-002", "case-003", "case-004")},
                "automatic_publications": 0,
            },
        }), encoding="utf-8")
        (root / "safetrace/agent_queue/artifacts/release-report.json").write_text(json.dumps({
            "status": "pass",
            "workers": {"count": 12, "implemented": [f"worker-{i}" for i in range(12)]},
            "metrics": {"auto_approved": 0, "awaiting_human": 12, "receipts": 12},
            "evaluation": {"status": "pass", "passed": 10, "total": 10, "unsafe_accepted": 0},
            "boundaries": {
                "proposal_only": True, "autonomous_publication": False,
                "autonomous_contact": False, "autonomous_referral": False,
                "restricted_partner_data": False,
            },
        }), encoding="utf-8")
        (root / "safetrace/investigation_desk/artifacts/release-report.json").write_text(json.dumps({
            "status": "pass",
            "views": {"count": 11, "implemented": [f"view-{i}" for i in range(11)]},
            "roles": {"synthetic_authenticated_sessions": True, "production_identity_provider_configured": False},
            "workflow": {
                "claim_review_state": "approved", "agent_proposal_status": "accepted_for_review",
                "publication_status_after_correction": "stale",
                "public_export": {
                    "internal_comments_included": False, "internal_tasks_included": False,
                    "agent_proposals_included": False,
                },
            },
            "audit": {"status": "pass", "events": 14},
            "prohibited_actions": {
                "investigator_publish_approval": "Role investigator cannot perform approve_publication",
                "unauthenticated_action": "Authenticated internal session required",
            },
            "boundaries": {
                "authoritative_internal_system": True, "public_portal_separate": True,
                "agent_proposals_auto_publish": False, "production_auth_ready": False,
                "restricted_partner_data": False,
            },
        }), encoding="utf-8")
        (root / "safetrace/case_004_reference/artifacts/release-report.json").write_text(json.dumps({
            "status": "pass",
            "counts": {"sources": 11, "measures": 5, "claims": 5, "agent_proposals": 4, "desk_views": 11},
            "source_backfill": {"sources_registered": 11, "original_bytes_backfilled": 0, "publication_allowed": False},
            "workflow": {
                "human_reviewed_claims": 5, "agent_proposals_accepted_for_review": 4,
                "publication_requests": 0, "audit": {"status": "pass", "events": 60},
            },
            "benchmark": {
                "target_met_in_fixture": True, "observed_human_time_measurement": False,
                "real_partner_impact_claimed": False,
            },
            "comprehension": {
                "participant_count": 0, "observed_study_completed": False,
                "concepts": ["fact", "status", "attribution", "value"],
            },
            "boundaries": {
                "technical_reference_complete": True, "new_publication_allowed": False,
                "real_partner_impact_claimed": False,
                "external_comprehension_study_completed": False,
                "restricted_partner_data": False,
            },
        }), encoding="utf-8")
        slots = [
            {
                "discipline": f"discipline-{i}", "purpose": "Independent review purpose",
                "minimum_qualification": "Qualified external reviewer", "independent_required": True,
                "external_reviewer_id": None, "conflict_declaration_id": None, "status": "unassigned",
            }
            for i in range(7)
        ]
        packets = [{"id": f"packet-{i}"} for i in range(7)]
        exercises = [{"id": f"exercise-{i}", "mode": "synthetic_dry_run"} for i in range(3)]
        protocols = [
            {"id": "workflow", "consent_required": True, "status": "ready_for_ethics_privacy_review"},
            {"id": "comprehension", "consent_required": True, "status": "ready_for_ethics_privacy_review"},
        ]
        backfill_sources = [{"source_id": f"source-{i}"} for i in range(11)]
        (root / "safetrace/review_readiness/artifacts/review-readiness-report.json").write_text(json.dumps({
            "status": "pass",
            "review": {
                "disciplines": [f"discipline-{i}" for i in range(7)],
                "slots": slots, "packets": packets,
                "external_reviews_completed": 0, "external_approvals": 0,
                "conflict_declarations_received": 0,
            },
            "findings": {"open_total": 7, "unresolved_critical": 1, "unresolved_high": 3},
            "exercises": {"items": exercises, "synthetic_dry_runs": 3, "externally_observed": 0},
            "study_protocols": protocols,
            "source_backfill": {
                "sources": backfill_sources, "automatic_publication_after_backfill": False,
                "renewed_human_review_required": True,
            },
            "decision": {
                "ready_to_invite_reviewers": True, "external_reviews_completed": 0,
                "external_approvals": 0, "partner_pilot_gate_open": False,
                "restricted_data_gate_open": False,
            },
            "boundaries": {
                "independent_review_completed": False, "external_approval_present": False,
                "partner_named": False, "partner_pilot_gate_open": False,
                "restricted_data_gate_open": False, "production_security_approved": False,
            },
        }), encoding="utf-8")

    def test_release_is_review_ready_but_not_externally_approved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            status = validate_repository(root)
            self.assertTrue(status["release_ready"])
            self.assertFalse(status["live_partner_ready"])
            report = status["review_readiness"]["release_evidence"]
            self.assertEqual(report["review"]["external_approvals"], 0)
            self.assertFalse(report["boundaries"]["independent_review_completed"])
            self.assertIn("No external review", status["truthful_status"])

    def test_missing_or_failed_review_report_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/review_readiness/artifacts/review-readiness-report.json"
            report.unlink()
            self.assertFalse(validate_repository(root)["release_ready"])
            report.write_text(json.dumps({"status": "fail"}), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

    def test_fabricated_external_approval_or_completed_review_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/review_readiness/artifacts/review-readiness-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["review"]["external_approvals"] = 1
            payload["decision"]["external_approvals"] = 1
            payload["boundaries"]["external_approval_present"] = True
            report.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/review_readiness/artifacts/review-readiness-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["boundaries"]["independent_review_completed"] = True
            report.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

    def test_open_critical_findings_and_closed_pilot_gate_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/review_readiness/artifacts/review-readiness-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["findings"]["unresolved_critical"] = 0
            report.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/review_readiness/artifacts/review-readiness-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["decision"]["partner_pilot_gate_open"] = True
            payload["boundaries"]["partner_pilot_gate_open"] = True
            report.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

    def test_status_file_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            output = root / "status.json"
            write_release_status(root, output)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["release"],
                "v1.8-independent-review-readiness",
            )


if __name__ == "__main__":
    unittest.main()
