import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ImpactMission001Tests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
        self.page = (ROOT / "index.html").read_text(encoding="utf-8").lower()

    def test_three_selected_indicators(self):
        ids = {item["indicator_id"] for item in self.data["indicators"]}
        self.assertEqual(ids, {
            "unemployment-rate-june-2026",
            "poverty-risk-2025",
            "onshore-wind-capacity-2030-gap",
        })

    def test_every_indicator_keeps_definition_and_official_source(self):
        for item in self.data["indicators"]:
            self.assertTrue(item["definition_caveat"])
            self.assertTrue(item["source"]["url"].startswith("https://"))
            self.assertIn("official", item["source"]["evidence_status"])

    def test_hypotheses_are_not_findings(self):
        self.assertGreaterEqual(len(self.data["impact_hypotheses"]), 3)
        self.assertTrue(all(item["evidence_status"] == "to_test" for item in self.data["impact_hypotheses"]))
        self.assertIn("not a proven causal chain", self.data["boundary"])

    def test_personal_impact_contract(self):
        contract = self.data["success_contract"]
        self.assertEqual(contract["first_cycle"]["readers"], 10)
        self.assertEqual(contract["first_cycle"]["external_challenges"], 3)
        self.assertEqual(contract["first_cycle"]["expert_conversations"], 1)
        self.assertFalse(contract["publication_allowed"])
        self.assertTrue(contract["human_review_required"])

    def test_browser_local_and_no_tracking(self):
        self.assertIn("localstorage", self.page)
        self.assertNotIn("google-analytics", self.page)
        self.assertNotIn("gtag(", self.page)
        self.assertNotIn("posthog", self.page)
        self.assertNotIn("mixpanel", self.page)


if __name__ == "__main__":
    unittest.main()
