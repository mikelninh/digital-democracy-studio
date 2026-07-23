from __future__ import annotations

import unittest
from pathlib import Path

from safetrace.law_fairness.model import build_public_assessment, load_case


class LawFairnessTests(unittest.TestCase):
    @property
    def case_path(self) -> Path:
        return Path(__file__).parents[1] / "data/case_004.json"

    def test_case_loads_and_has_sources_for_every_measure(self) -> None:
        case = load_case(self.case_path)
        self.assertEqual(len(case["measures"]), 5)
        self.assertTrue(all(measure.source_ids for measure in case["measures"]))

    def test_inherited_measures_are_not_attributed_to_merz_government(self) -> None:
        case = load_case(self.case_path)
        inherited = {
            measure.id: measure
            for measure in case["measures"]
            if measure.origin in {"prior_legislature", "preexisting_statutory_formula"}
        }
        self.assertFalse(inherited["child-benefit-and-allowance-2026"].attributable_to_current_government)
        self.assertFalse(inherited["basic-security-rate-freeze-2026"].attributable_to_current_government)

    def test_no_single_moral_fairness_score_is_published(self) -> None:
        case = load_case(self.case_path)
        self.assertIsNone(case["methodology"]["aggregate_fairness_score"])
        public = build_public_assessment(case)
        self.assertNotIn("fairness_score", public)

    def test_core_claim_verdicts_are_careful(self) -> None:
        case = load_case(self.case_path)
        verdicts = {claim.id: claim.verdict for claim in case["claim_tests"]}
        self.assertEqual(verdicts["claim-business-relief"], "supported")
        self.assertEqual(verdicts["claim-nominal-benefit-cut"], "not_supported")
        self.assertEqual(verdicts["claim-stricter-poor-households"], "supported")
        self.assertEqual(verdicts["claim-only-rich"], "partly_supported")

    def test_indirect_effects_keep_uncertainty_visible(self) -> None:
        case = load_case(self.case_path)
        indirect = [impact for measure in case["measures"] for impact in measure.impacts if impact.directness == "indirect"]
        self.assertTrue(indirect)
        self.assertTrue(all(impact.confidence in {"medium", "low", "high"} for impact in indirect))
        self.assertTrue(any(impact.effect == "uncertain" for impact in indirect))


if __name__ == "__main__":
    unittest.main()
