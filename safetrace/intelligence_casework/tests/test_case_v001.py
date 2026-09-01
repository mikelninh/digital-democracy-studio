from __future__ import annotations

import json
import unittest
from pathlib import Path

from safetrace.intelligence_casework.validate_case import validate

ROOT = Path(__file__).resolve().parents[1]
CASE = json.loads((ROOT / "data" / "case_v001.json").read_text(encoding="utf-8"))


class IntelligenceCaseworkV001Tests(unittest.TestCase):
    def test_case_passes_quality_gates(self) -> None:
        self.assertEqual(validate(CASE), [])

    def test_screening_homonym_is_not_same_as(self) -> None:
        screening = CASE["screening"]
        self.assertFalse(screening["same_as"])
        self.assertGreaterEqual(len(screening["reasons_against_merge"]), 2)

    def test_every_relationship_has_evidence_and_claim(self) -> None:
        for relationship in CASE["relationships"]:
            self.assertTrue(relationship["evidence"])
            self.assertTrue(relationship["claim_id"])

    def test_contradictions_have_next_steps(self) -> None:
        self.assertGreaterEqual(len(CASE["contradictions"]), 2)
        for contradiction in CASE["contradictions"]:
            self.assertTrue(contradiction["next_step"])

    def test_risk_signal_cannot_become_accusation_automatically(self) -> None:
        self.assertFalse(CASE["quality_controls"]["accusation_from_risk_signal"])

    def test_negative_evidence_is_explicitly_bounded(self) -> None:
        claim = next(item for item in CASE["claims"] if item["id"] == "C9")
        self.assertEqual(claim["state"], "negative_evidence")
        self.assertIn("do not establish absence", claim["limitation"])

    def test_indirect_ownership_arithmetic(self) -> None:
        meridian_share = 0.70
        asterion_in_meridian = 0.60
        helix_in_meridian = 0.40
        self.assertAlmostEqual(meridian_share * asterion_in_meridian, 0.42)
        self.assertAlmostEqual(meridian_share * helix_in_meridian, 0.28)


if __name__ == "__main__":
    unittest.main()
