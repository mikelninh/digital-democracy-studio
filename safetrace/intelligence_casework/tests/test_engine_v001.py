from __future__ import annotations
import json, unittest
from pathlib import Path
from safetrace.intelligence_casework.engine import investigate, render_markdown, validate_input

ROOT=Path(__file__).resolve().parents[1]
INPUT=json.loads((ROOT/"data"/"investigation_input_v001.json").read_text(encoding="utf-8"))

class WorkingInvestigationV001Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r=investigate(INPUT)
    def test_input_valid(self): self.assertEqual(validate_input(INPUT),[])
    def test_end_to_end_decision(self):
        self.assertEqual(self.r["status"],"completed"); self.assertEqual(self.r["executive_result"]["decision"],"ENHANCED_DUE_DILIGENCE_REQUIRED")
    def test_ownership_is_computed(self):
        d={x["owner_id"]:x["effective_interest"] for x in self.r["ownership"]["paths"]}
        self.assertAlmostEqual(d["E2"],.70); self.assertAlmostEqual(d["E3"],.42); self.assertAlmostEqual(d["E4"],.28)
    def test_ubo_gap(self):
        g=self.r["ownership"]["beneficial_ownership_gaps"]; self.assertEqual(g[0]["entity_id"],"E4"); self.assertAlmostEqual(g[0]["effective_interest"],.28)
    def test_sanctions_homonym_rejected(self):
        s=self.r["screening"][0]; self.assertFalse(s["same_as"]); self.assertIn("dob",s["conflicting_identifiers"]); self.assertFalse(self.r["executive_result"]["confirmed_sanctions_match"])
    def test_payment_anomaly_not_accusation(self):
        x=self.r["payment_anomalies"][0]; self.assertEqual(x["changed_beneficiary_id"],"E7"); self.assertIn("not proof of fraud",x["assessment"])
    def test_director_conflict(self): self.assertTrue(self.r["contradictions"][0]["next_action"])
    def test_negative_evidence_bounded(self): self.assertIn("does not prove",self.r["negative_evidence"][0]["assessment"])
    def test_asset_types_separate(self):
        d={}
        for x in self.r["asset_interests"]: d.setdefault(x["asset_id"],set()).add(x["interest_type"])
        self.assertEqual(d["AS1"],{"LEGAL_OWNER_OF","SECURITY_INTEREST_IN","OPERATES_AT"}); self.assertEqual(d["AS2"],{"LEGAL_OWNER_OF","LESSEE_OF"})
    def test_report_clear(self):
        m=render_markdown(self.r); self.assertIn("## Executive finding",m); self.assertIn("## Next investigative actions",m)

if __name__=="__main__": unittest.main()
