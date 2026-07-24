from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("wohlstandslabor_validate", ROOT / "validate.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
validate = MODULE.validate


class WohlstandslaborTests(unittest.TestCase):
    def test_release_contract(self) -> None:
        report = validate(ROOT)
        self.assertEqual(report["status"], "pass", report)
        self.assertTrue(all(report["checks"].values()))

    def test_meaningful_public_source_coverage(self) -> None:
        report = validate(ROOT)
        self.assertGreaterEqual(report["counts"]["sources"], 12)
        self.assertEqual(report["counts"]["policies"], 4)
        self.assertEqual(report["counts"]["lenses"], 7)


if __name__ == "__main__":
    unittest.main()
