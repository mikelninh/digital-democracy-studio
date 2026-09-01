from __future__ import annotations

import json
import unittest
from pathlib import Path

from safetrace.venatic_challenge.collection import prioritize
from safetrace.venatic_challenge.evaluate import evaluate
from safetrace.venatic_challenge.run_budgeted import run_budgeted


BASE = Path(__file__).resolve().parents[1]


class CollectionPriorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case = json.loads((BASE / "case_v002.json").read_text(encoding="utf-8"))
        cls.gold = json.loads((BASE / "gold_answer.json").read_text(encoding="utf-8"))

    def test_ranker_uses_full_five_source_budget(self) -> None:
        ranked = prioritize(self.case)
        self.assertEqual(len(ranked), 5)
        self.assertEqual(len({row["source_id"] for row in ranked}), 5)

    def test_ranker_rejects_duplicate_media_noise(self) -> None:
        selected = {row["source_id"] for row in prioritize(self.case)}
        self.assertNotIn("S27", selected)
        self.assertNotIn("S26", selected)

    def test_ranker_selects_three_or_more_gold_high_value_sources(self) -> None:
        selected = {row["source_id"] for row in prioritize(self.case)}
        preferred = set(self.gold["preferred_optional_collection"])
        self.assertGreaterEqual(len(selected & preferred), 3)

    def test_budgeted_run_reaches_analyst_grade_without_critical_failure(self) -> None:
        submission, _ = run_budgeted(self.case)
        result = evaluate(submission, self.gold)
        self.assertGreaterEqual(result["score"], 90)
        self.assertEqual(result["critical_failures"], [])
        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
