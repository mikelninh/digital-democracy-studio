from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from safetrace.policy_platform.refresh import run


class RefreshTests(unittest.TestCase):
    def build_root(self, tmp: Path, marker: str = "6,2") -> tuple[Path, Path]:
        root = tmp / "safetrace"
        (root / "policy_platform").mkdir(parents=True)
        (root / "open_policy_api" / "v1").mkdir(parents=True)
        registry = {
            "sources": [
                {
                    "source_id": "ba",
                    "publisher": "BA",
                    "url": "https://example.test/ba",
                    "required_markers": ["Arbeitslosenquote", marker],
                }
            ]
        }
        catalog = {"sources": [{"source_id": "ba", "url": "https://example.test/ba"}]}
        (root / "policy_platform" / "source_registry.json").write_text(json.dumps(registry), encoding="utf-8")
        (root / "open_policy_api" / "v1" / "catalog.json").write_text(json.dumps(catalog), encoding="utf-8")
        fixtures = tmp / "fixtures"
        fixtures.mkdir()
        (fixtures / "ba.html").write_text("<html><body>Arbeitslosenquote 6,2 Prozent</body></html>", encoding="utf-8")
        return root, fixtures

    def test_verified_fixture_creates_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            root, fixtures = self.build_root(tmp)
            report = run(root, tmp / "out", fixtures)
            self.assertEqual(report["status"], "verified_no_material_marker_change")
            self.assertFalse(report["publication_allowed"])
            self.assertTrue((tmp / "out" / "receipts" / "ba.json").exists())

    def test_missing_marker_requires_review_but_does_not_publish(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            root, fixtures = self.build_root(tmp, marker="7,0")
            report = run(root, tmp / "out", fixtures)
            self.assertEqual(report["status"], "review_required")
            self.assertFalse(report["publication_allowed"])
            self.assertEqual(report["counts"]["review_required"], 1)


if __name__ == "__main__":
    unittest.main()
