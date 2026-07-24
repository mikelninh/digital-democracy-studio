from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from safetrace.review_readiness.build_review_pack import build
from safetrace.review_readiness.model import ReviewSlot, StudyProtocol


class ReviewReadinessTests(unittest.TestCase):
    def test_review_dossier_is_complete_but_external_approval_is_zero(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = build(safetrace_root, output)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(len(report["review"]["disciplines"]), 7)
            self.assertEqual(len(report["review"]["slots"]), 7)
            self.assertEqual(len(report["review"]["packets"]), 7)
            self.assertEqual(report["review"]["external_reviews_completed"], 0)
            self.assertEqual(report["review"]["external_approvals"], 0)
            self.assertEqual(report["review"]["conflict_declarations_received"], 0)
            self.assertTrue(all(slot["status"] == "unassigned" for slot in report["review"]["slots"]))
            self.assertTrue(all(slot["external_reviewer_id"] is None for slot in report["review"]["slots"]))

    def test_open_critical_and_high_findings_keep_pilot_gate_closed(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            report = build(safetrace_root, Path(directory))
            self.assertGreaterEqual(report["findings"]["unresolved_critical"], 1)
            self.assertGreaterEqual(report["findings"]["unresolved_high"], 1)
            self.assertTrue(report["decision"]["ready_to_invite_reviewers"])
            self.assertFalse(report["decision"]["partner_pilot_gate_open"])
            self.assertFalse(report["decision"]["restricted_data_gate_open"])
            self.assertFalse(report["boundaries"]["independent_review_completed"])
            self.assertFalse(report["boundaries"]["external_approval_present"])
            self.assertFalse(report["boundaries"]["production_security_approved"])

    def test_exercises_and_studies_are_dry_runs_and_review_protocols(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            report = build(safetrace_root, Path(directory))
            self.assertEqual(report["exercises"]["synthetic_dry_runs"], 3)
            self.assertEqual(report["exercises"]["externally_observed"], 0)
            self.assertTrue(all(item["mode"] == "synthetic_dry_run" for item in report["exercises"]["items"]))
            self.assertEqual(len(report["study_protocols"]), 2)
            self.assertTrue(all(item["consent_required"] for item in report["study_protocols"]))
            self.assertTrue(all(item["status"] == "ready_for_ethics_privacy_review" for item in report["study_protocols"]))

    def test_case004_backfill_plan_requires_all_eleven_sources_and_renewed_review(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            report = build(safetrace_root, Path(directory))
            backfill = report["source_backfill"]
            self.assertEqual(len(backfill["sources"]), 11)
            self.assertTrue(all(item["status"] == "pending_controlled_acquisition" for item in backfill["sources"]))
            self.assertFalse(backfill["automatic_publication_after_backfill"])
            self.assertTrue(backfill["renewed_human_review_required"])

    def test_artifacts_are_hashed_machine_readable_and_pdf(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = build(safetrace_root, output)
            self.assertTrue(report["artifact_hashes"])
            self.assertTrue(all(len(value) == 64 for value in report["artifact_hashes"].values()))
            self.assertTrue((output / "review-readiness-dossier.pdf").read_bytes().startswith(b"%PDF"))
            findings = json.loads((output / "finding-register.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(findings["open_total"], 1)
            packets = json.loads((output / "review-packets.json").read_text(encoding="utf-8"))
            self.assertEqual(len(packets["packets"]), 7)

    def test_completed_review_cannot_exist_without_real_external_identity(self) -> None:
        slot = ReviewSlot(
            "security",
            "Review security controls independently and document material findings.",
            "Independent application-security specialist.",
            True,
            status="completed",
        )
        with self.assertRaisesRegex(ValueError, "reviewer identity"):
            slot.validate()

    def test_v18_cannot_self_approve_external_study(self) -> None:
        protocol = StudyProtocol(
            "protocol:test",
            "workflow_benchmark",
            "Measure a controlled workflow without overstating external impact.",
            ("Qualified participant",),
            True,
            ("duration",),
            ("private address",),
            ("median time",),
            ("Stop on incident",),
            "approved",
        )
        with self.assertRaisesRegex(ValueError, "cannot self-approve"):
            protocol.validate()


if __name__ == "__main__":
    unittest.main()
