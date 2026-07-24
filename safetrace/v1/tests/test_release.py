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
        ]
        for component in components:
            (root / "safetrace" / component).mkdir(parents=True, exist_ok=True)
        for path in (
            "governance/data", "pilot/data", "core/schemas", "evidence_vault/schemas",
            "evidence_vault/artifacts", "claim_ledger/artifacts", "agent_queue/artifacts",
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
        (root / "safetrace/core/schemas/safetrace-core-1.2.schema.json").write_text("{}", encoding="utf-8")
        (root / "safetrace/evidence_vault/schemas/evidence-vault-contracts-1.3.json").write_text("{}", encoding="utf-8")
        (root / "safetrace/claim_ledger/artifacts/claim-ledger-contracts-1.4.json").write_text("{}", encoding="utf-8")
        (root / "safetrace/agent_queue/artifacts/agent-queue-contracts-1.5.json").write_text("{}", encoding="utf-8")

        (root / "safetrace/core/migration-report.json").write_text(
            json.dumps({
                "status": "pass",
                "target_schema": "safetrace.core/1.2",
                "cases": {case_id: {} for case_id in ("case-001", "case-002", "case-003", "case-004")},
            }),
            encoding="utf-8",
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
            }),
            encoding="utf-8",
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
            }),
            encoding="utf-8",
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
            }),
            encoding="utf-8",
        )

    def test_release_is_ready_but_not_live_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            status = validate_repository(root)
            self.assertTrue(status["release_ready"])
            self.assertFalse(status["live_partner_ready"])
            self.assertTrue(status["components"]["agent_queue"])
            self.assertEqual(status["agent_queue"]["release_evidence"]["status"], "pass")
            self.assertIn("Agents cannot approve", status["truthful_status"])

    def test_missing_or_failed_agent_report_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/agent_queue/artifacts/release-report.json"
            report.unlink()
            self.assertFalse(validate_repository(root)["release_ready"])
            report.write_text(json.dumps({"status": "fail"}), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

    def test_unsafe_agent_acceptance_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/agent_queue/artifacts/release-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["evaluation"]["unsafe_accepted"] = 1
            report.write_text(json.dumps(payload), encoding="utf-8")
            self.assertFalse(validate_repository(root)["release_ready"])

    def test_autonomous_approval_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._make_repository(root)
            report = root / "safetrace/agent_queue/artifacts/release-report.json"
            payload = json.loads(report.read_text(encoding="utf-8"))
            payload["metrics"]["auto_approved"] = 1
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
                "v1.5-auditable-agent-task-queue",
            )


if __name__ == "__main__":
    unittest.main()
