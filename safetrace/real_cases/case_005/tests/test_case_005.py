from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from safetrace.real_cases.case_005.build_case import build, load_config


ROOT = Path(__file__).parents[1]


class Case005Tests(unittest.TestCase):
    def _fixtures(self, root: Path) -> Path:
        config = load_config(ROOT)
        fixture_dir = root / "fixtures"
        fixture_dir.mkdir(parents=True)
        for source in config["sources"]:
            markers = " ".join(source["required_markers"])
            (fixture_dir / f"{source['source_id']}.html").write_text(
                f"<!doctype html><html><body><main><h1>{source['title']}</h1><p>{markers}</p></main></body></html>",
                encoding="utf-8",
            )
        return fixture_dir

    def test_official_registry_is_narrow_and_public(self) -> None:
        config = load_config(ROOT)
        self.assertEqual(config["case_id"], "case-005")
        self.assertEqual(len(config["sources"]), 4)
        self.assertEqual(config["acquisition_review"]["reviewed_by"], "Michael Ninh")
        for source in config["sources"]:
            self.assertTrue(source["canonical_url"].startswith("https://"))
            self.assertEqual(source["source_rank"], "primary_official")
            self.assertEqual(source["expected_content_types"], ["text/html"])
            self.assertTrue(source["required_markers"])

    def test_fixture_build_creates_real_vault_structure_but_blocks_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            fixture_dir = self._fixtures(base)
            output = base / "artifacts"
            report = build(
                ROOT,
                output,
                fixture_dir=fixture_dir,
                acquired_at="2026-07-24T12:00:00+00:00",
            )
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["source_acquisition"]["official_sources"], 4)
            self.assertEqual(report["source_acquisition"]["original_receipts"], 4)
            self.assertTrue(report["source_acquisition"]["all_markers_verified"])
            self.assertEqual(report["vault_integrity"]["status"], "pass")
            self.assertEqual(report["claim_ledger"]["claims"], 4)
            self.assertEqual(report["claim_ledger"]["vault_backed_current_claims"], 4)
            self.assertEqual(report["review"]["pending_review_tasks"], 12)
            self.assertFalse(report["publication"]["allowed"])
            self.assertIn("named human review is pending", report["truthful_status"])
            self.assertTrue((output / "index.html").exists())
            self.assertTrue((output / "public-draft.json").exists())
            self.assertTrue((output / "review-candidate.json").exists())
            self.assertEqual(len(list((output / "vault/receipts").glob("*.json"))), 4)

    def test_missing_marker_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            fixture_dir = self._fixtures(base)
            broken = fixture_dir / "case005-bkgg-current-law.html"
            broken.write_text("<html><body>wrong legal text</body></html>", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Required markers missing"):
                build(
                    ROOT,
                    base / "artifacts",
                    fixture_dir=fixture_dir,
                    acquired_at="2026-07-24T12:00:00+00:00",
                )

    def test_public_draft_never_self_publishes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            fixture_dir = self._fixtures(base)
            output = base / "artifacts"
            build(ROOT, output, fixture_dir=fixture_dir, acquired_at="2026-07-24T12:00:00+00:00")
            draft = json.loads((output / "public-draft.json").read_text(encoding="utf-8"))
            self.assertFalse(draft["publication_allowed"])
            self.assertEqual(draft["status"], "source_verified_awaiting_named_human_review")
            self.assertFalse(draft["impact_measurement"]["network_submission"])
            self.assertEqual(draft["impact_measurement"]["aggregate_results_observed"], 0)


if __name__ == "__main__":
    unittest.main()
