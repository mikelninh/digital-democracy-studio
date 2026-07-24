from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from safetrace.case_004_reference.build_reference import build


class Case004ReferenceTests(unittest.TestCase):
    def test_reference_case_is_complete_but_new_publication_is_blocked(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = build(safetrace_root, output)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["counts"]["sources"], 11)
            self.assertEqual(report["counts"]["measures"], 5)
            self.assertEqual(report["counts"]["claims"], 5)
            self.assertEqual(report["source_backfill"]["original_bytes_backfilled"], 0)
            self.assertFalse(report["boundaries"]["new_publication_allowed"])

    def test_all_material_claims_are_human_reviewed_and_agents_remain_proposals(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            report = build(safetrace_root, Path(directory))
            self.assertEqual(report["workflow"]["human_reviewed_claims"], 5)
            self.assertEqual(report["workflow"]["agent_proposals_accepted_for_review"], 4)
            self.assertEqual(report["workflow"]["publication_requests"], 0)
            self.assertEqual(report["workflow"]["audit"]["status"], "pass")
            self.assertEqual(report["counts"]["desk_views"], 11)

    def test_benchmark_and_comprehension_are_not_misrepresented_as_real_impact(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            report = build(safetrace_root, Path(directory))
            benchmark = report["benchmark"]
            self.assertTrue(benchmark["target_met_in_fixture"])
            self.assertFalse(benchmark["observed_human_time_measurement"])
            self.assertFalse(benchmark["real_partner_impact_claimed"])
            comprehension = report["comprehension"]
            self.assertEqual(comprehension["participant_count"], 0)
            self.assertFalse(comprehension["observed_study_completed"])
            self.assertGreaterEqual(len(comprehension["concepts"]), 4)

    def test_reference_artifacts_are_machine_and_human_readable(self) -> None:
        safetrace_root = Path(__file__).parents[2]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            build(safetrace_root, output)
            pack = json.loads((output / "case-004-reference-pack.json").read_text(encoding="utf-8"))
            self.assertEqual(pack["edition"], "technical_reference_not_new_publication")
            self.assertEqual(len(pack["claims"]), 5)
            self.assertEqual(len(pack["sources"]), 11)
            pdf = output / "case-004-reference-pack.pdf"
            self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))
            monitoring = json.loads((output / "monitoring-manifest.json").read_text(encoding="utf-8"))
            self.assertFalse(monitoring["automatic_public_effect"])
            self.assertTrue(monitoring["human_review_required"])


if __name__ == "__main__":
    unittest.main()
