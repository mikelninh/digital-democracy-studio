import json
import tempfile
import unittest
from pathlib import Path

from safetrace.intelligence_casework.live_investigator import DEFAULT_CASE, run


class LiveInvestigatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)
        self.result = run(DEFAULT_CASE, self.out)

    def tearDown(self):
        self.tmp.cleanup()

    def test_outputs_are_generated(self):
        for name in ("result.json", "report.md", "graph.json", "findings.json"):
            self.assertTrue((self.out / name).exists(), name)

    def test_sanctions_homonym_is_rejected_not_accused(self):
        screen = self.result["sanctions_screening"][0]
        self.assertEqual(screen["result"], "rejected_match")
        self.assertIn("dob", screen["conflicting_identifiers"])
        self.assertIn("nationality", screen["conflicting_identifiers"])
        self.assertEqual(screen["conclusion"], "No sanctions linkage established.")

    def test_indirect_ownership_math_is_correct_and_bounded(self):
        interest = next(x for x in self.result["indirect_ownership"] if x["owner"] == "ent:asterion")
        self.assertEqual(interest["percent"], 42.0)
        self.assertEqual(interest["interpretation"], "economic_interest_not_necessarily_control")

    def test_asset_roles_are_not_collapsed(self):
        rels = self.result["relationships"]
        kinds = {(r["source"], r["kind"], r["target"]) for r in rels}
        self.assertIn(("ent:property", "OWNS_ASSET", "ent:site"), kinds)
        self.assertIn(("ent:bank", "SECURITY_INTEREST", "ent:site"), kinds)
        self.assertIn(("ent:northstar", "OPERATES_AT", "ent:site"), kinds)

    def test_contradiction_stays_unresolved_with_next_step(self):
        contradiction = self.result["contradictions"][0]
        self.assertEqual(contradiction["status"], "unresolved")
        self.assertTrue(contradiction["next_step"])
        self.assertEqual(len(contradiction["evidence"]), 2)

    def test_material_findings_keep_caveats_and_evidence(self):
        material = [x for x in self.result["findings"] if x["severity"] in {"high", "medium"}]
        self.assertGreaterEqual(len(material), 3)
        for finding in material:
            self.assertTrue(finding["evidence"])
            self.assertTrue(finding["caveat"])
            self.assertTrue(finding["next_step"])

    def test_report_contains_clear_decision_sections(self):
        report = (self.out / "report.md").read_text(encoding="utf-8")
        for section in ("Executive judgement", "Key findings", "Priority collection plan", "Bottom line"):
            self.assertIn(section, report)
        self.assertNotIn("confirmed sanctions evasion", report.lower())
        self.assertNotIn("fraud proven", report.lower())

    def test_result_is_reproducible(self):
        second = self.out / "second"
        r2 = run(DEFAULT_CASE, second)
        self.assertEqual(self.result["metrics"], r2["metrics"])
        self.assertEqual(self.result["findings"], r2["findings"])


if __name__ == "__main__":
    unittest.main()
