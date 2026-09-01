from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from safetrace.venatic_challenge.evaluate import evaluate


BASE = Path(__file__).resolve().parents[1]


class AnalystChallengeEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gold = json.loads((BASE / "gold_answer.json").read_text(encoding="utf-8"))
        cls.reference = json.loads((BASE / "fixtures" / "gold_submission.json").read_text(encoding="utf-8"))

    def test_reference_submission_scores_100(self) -> None:
        result = evaluate(self.reference, self.gold)
        self.assertEqual(result["score"], 100)
        self.assertTrue(result["passed"])
        self.assertEqual(result["critical_failures"], [])

    def test_critical_failure_caps_score_even_if_rest_is_polished(self) -> None:
        submission = copy.deepcopy(self.reference)
        submission["critical_failure_flags"]["sanctions_match_claimed"] = True
        result = evaluate(submission, self.gold)
        self.assertLessEqual(result["score"], 49)
        self.assertFalse(result["passed"])
        self.assertIn("sanctions_match_claimed", result["critical_failures"])

    def test_unresolved_nominee_gap_must_be_preserved(self) -> None:
        submission = copy.deepcopy(self.reference)
        submission["ownership"]["beneficial_ownership_complete"] = True
        submission["uncertainty"]["unresolved_items"] = []
        result = evaluate(submission, self.gold)
        checks = {row["check"]: row for row in result["detail"]}
        self.assertFalse(checks["Beneficial ownership remains incomplete"]["passed"])
        self.assertFalse(checks["Nominee UBO gap surfaced"]["passed"])
        self.assertLess(result["score"], 100)

    def test_asset_roles_are_scored_separately(self) -> None:
        submission = copy.deepcopy(self.reference)
        submission["assets"]["legal_owner"] = "Meridian Atlas Trading GmbH"
        result = evaluate(submission, self.gold)
        checks = {row["check"]: row for row in result["detail"]}
        self.assertFalse(checks["Property legal owner"]["passed"])
        self.assertTrue(checks["Security holder separated"]["passed"])
        self.assertTrue(checks["Operator/lessee separated"]["passed"])

    def test_collection_plan_rewards_information_value(self) -> None:
        submission = copy.deepcopy(self.reference)
        submission["optional_sources_selected"] = ["S20", "S21", "S23", "S26", "S27"]
        result = evaluate(submission, self.gold)
        checks = {row["check"]: row for row in result["detail"]}
        self.assertFalse(checks["High-value optional collection"]["passed"])


if __name__ == "__main__":
    unittest.main()
