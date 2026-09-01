from __future__ import annotations

import json
import unittest
from pathlib import Path

from safetrace.intelligence_casework.validate_case import validate, validate_asset_trace, validate_eval

ROOT = Path(__file__).resolve().parents[1]
CASE = json.loads((ROOT / "data" / "case_v001.json").read_text(encoding="utf-8"))
EVAL = json.loads((ROOT / "data" / "analyst_eval_v001.json").read_text(encoding="utf-8"))
ASSET_TRACE = json.loads((ROOT / "data" / "asset_trace_v001.json").read_text(encoding="utf-8"))


class IntelligenceCaseworkV001Tests(unittest.TestCase):
    def test_case_passes_quality_gates(self) -> None:
        self.assertEqual(validate(CASE), [])
        self.assertEqual(validate_eval(EVAL, CASE), [])
        self.assertEqual(validate_asset_trace(ASSET_TRACE), [])

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

    def test_analyst_evaluation_is_100_point_and_has_critical_fails(self) -> None:
        self.assertEqual(len(EVAL["items"]), 10)
        self.assertEqual(EVAL["scoring"]["total_points"], 100)
        self.assertGreaterEqual(len(EVAL["scoring"]["critical_fail_rules"]), 4)

    def test_asset_trace_separates_types_of_interest(self) -> None:
        interest_types = {item["type"] for item in ASSET_TRACE["interests"]}
        self.assertTrue({"LEGAL_OWNER_OF", "SECURITY_INTEREST_IN", "OPERATES_AT", "LESSEE_OF"}.issubset(interest_types))
        property_interests = [item for item in ASSET_TRACE["interests"] if item["to"] == "AS1"]
        self.assertEqual({item["type"] for item in property_interests}, {"LEGAL_OWNER_OF", "SECURITY_INTEREST_IN", "OPERATES_AT"})


if __name__ == "__main__":
    unittest.main()
