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
            "core", "evidence_vault", "claim_ledger", "agent_queue", "investigation_desk",
        ]
        for component in components:
            (root / "safetrace" / component).mkdir(parents=True, exist_ok=True)
        for path in (
            "governance/data", "pilot/data", "core/schemas", "evidence_vault/schemas",
            "evidence_vault/artifacts", "claim_ledger/artifacts", "agent_queue/artifacts",
            "investigation_desk/artifacts",
        ):
            (root / "safetrace" / path).mkdir(parents=True, exist_ok=True)

        (root / "safetrace/governance/data/readiness.json").write_text(
            (source_root / "governance/data/readiness.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (root / "safetrace/pilot/data/synthetic_pilot.json").write_text(
            (source_root / "pilot/data/synthetic_pilot.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        for path in (
            "core/schemas/safetrace-core-1.2.schema.json",
            "evidence_vault/schemas/evidence-vault-contracts-1.3.json",
            "claim_ledger/artifacts/claim-ledger-contracts-1.4.json",
            "agent_queue/artifacts/agent-queue-contracts-1.5.json",
            "investigation_desk/artifacts/investigation-desk-contracts-1.6.json",
        ):
            (root / "safetrace" / path).write_text("{}", encoding="utf-8")

        (root / "safetrace/core/migration-report.json").write_text(
            json.dumps({
                "status": "pass",
                "target_schema": "safetrace.core/1.2",
                "cases": {case_id: {} for case_id in ("case-001", "case-002", "case-003", "case-004")},
            }), encoding="utf-8",
        )
        (root / "safetrace/evidence_vault/artifacts/release-report.json").write_text(
            json.dumps({
                "status": "pass",
                "registry": {"status": "pass", "sources": 20, "minimum_expected_sources": 10},
                "demo": {
                    "receipt_chain_verified": True,
                    "material_change_alert": "material_change",
                    "integrity": {"status": "pass"},
                    "restore_integrity": {"status": "pass"},
                },
            }), encoding="utf-8",
        )
        (root / "safetrace/claim_ledger/artifacts/release-report.json").write_text(
            json.dumps({
                "status": "pass",
                "synthetic_fixture": {
                    "first_version_gate": {"ready": True},
                    "second_version_gate": {"ready": True},
                    "first_publication_status_after_correction": "stale",
                    "second_publication_status": "published",
                    "visible_correction": True,
                },
                "existing_case_migration": {
                    "status": "pass",
                    "cases": {case_id: {} for case_id in ("case-001", "case-002", "case-003", "case-004")},
                    "automatic_publications": 0,
                },
            }), encoding="utf-8",
        )
        (root / "safetrace/agent_queue/artifacts/release-report.json").write_text(
            json.dumps({
                "status": "pass",
                "workers": {"count": 12, "implemented": [f"worker-{i}" for i in range(12)]},
                "metrics": {"auto_approved": 0, "awaiting_human": 12, "receipts": 12},
                "evaluation": {"status": "pass", "passed": 10, "total": 10, "unsafe_accepted": 0},
                "boundaries": {
                    "proposal_only": True,
                    "autonomous_publication": False,
                    "autonomous_contact": False,
                    "autonomous_referral": False,
                    "restricted_partner_data": False,
                },
            }), encoding="utf-8",
        )
        (root / "safetrace/investigation_desk/artifacts/release-report.json").write_text(
            json.dumps({
                "status": "pass",
                "views": {"count": 11, "implemented": [f"view-{i}" for i in range(11)]},
                "roles": {
                    "synthetic_authenticated_sessions": True,
                    "production_identity_provider_configured": False,
                },
                "workflow": {
                    "claim_review_state": "approved",
                    "agent_proposal_status": "accepted_for_review",
                    "publication_status_after_correction": "stale",
                    "public_export": {
                        "internal_comments_included": False,
                        "internal_tasks_included": False,
                        "agent_proposals_included": False,
                    },
                },
                "audit": {"status": "pass", "events": 14},
                "prohibited_actions": {
                    "investigator_publish_approval": "Role investigator cannot perform approve_publication",
                    "unauthenticated_action": "Authenticated internal session required",
                },
                "boundaries": {
                    "authoritative_internal_system": True,
                    "public_portal_separate": True,
                    "agent_proposals_auto_publish": False,
                    "production_auth_ready": False,
                    "restricted_partner_data": False,
                },
            }), encoding="utf-8",
        )

    def test_release_is_ready_but_not_live_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            status = validate_repository(root)
            self.assertTrue(status["release_ready"])
            self.assertFalse(status["live_partner_ready"])
            self.assertTrue(status["components"]["investigation_desk"])
            self.assertEqual(status["investigation_desk"]["release_evidence"]["status"], "pass")
            self.assertIn("Production identity", status["truthful_status"])

    def test_missing_or_failed_desk_report_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/investigation_desk/artifacts/release-report.json"
            report.unlink()
            self.assertFalse(validate_repository(root)["release_ready"])
            report.write_text(json.dumps({"status": "fail"}), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

    def test_broken_audit_or_public_separation_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/investigation_desk/artifacts/release-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["audit"]["status"] = "fail"
            report.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/investigation_desk/artifacts/release-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["workflow"]["public_export"]["agent_proposals_included"] = True
            report.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

    def test_fabricated_production_auth_readiness_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/investigation_desk/artifacts/release-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["boundaries"]["production_auth_ready"] = True
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
                "v1.6-investigation-desk-foundation",
            )


if __name__ == "__main__":
    unittest.main()
