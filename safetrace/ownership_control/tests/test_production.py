from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from safetrace.ownership_control.production import investigate, run_case

HERE = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((HERE / "fixtures" / "golden_case.json").read_text(encoding="utf-8"))


class OwnershipControlProductionTests(unittest.TestCase):
    def test_unresolved_target_blocks_all_graph_propagation(self):
        case = copy.deepcopy(GOLDEN)
        target = next(item for item in case["entities"] if item["id"] == case["target_entity_id"])
        target["resolution_status"] = "ambiguous"

        result = investigate(case)

        self.assertEqual(result["schema_version"], "safetrace.ownership-control/1.1")
        self.assertEqual(result["economic_ownership"], [])
        self.assertEqual(result["voting_rights"], [])
        self.assertEqual(result["control_signals"], [])
        self.assertEqual(result["ubo_candidates"], [])
        self.assertEqual(result["screening_handoff"], [])
        self.assertFalse(result["decision_boundary"]["ownership_established"])
        self.assertTrue(any(item.get("type") == "target_identity_not_established" for item in result["unresolved"]))

    def test_confirmed_natural_person_candidates_are_handed_to_screening(self):
        result = investigate(copy.deepcopy(GOLDEN))
        handoff = {item["entity_id"]: item for item in result["screening_handoff"]}

        self.assertEqual(result["schema_version"], "safetrace.ownership-control/1.1")
        self.assertEqual(set(handoff), {"alice", "carol"})
        self.assertEqual(handoff["alice"]["identity_status"], "confirmed")
        self.assertEqual(handoff["alice"]["identifiers"]["dob"], "1980-01-01")
        self.assertIn("economic_ownership_threshold", handoff["alice"]["candidate_grounds"])
        self.assertIn("documented_control_right", handoff["carol"]["candidate_grounds"])
        self.assertTrue(all(item["handoff_status"] == "ready_for_authoritative_screening" for item in handoff.values()))
        self.assertTrue(all("not a sanctions match" in item["boundary"] for item in handoff.values()))

    def test_non_candidate_confirmed_person_is_not_handed_off(self):
        result = investigate(copy.deepcopy(GOLDEN))
        ids = {item["entity_id"] for item in result["screening_handoff"]}
        self.assertNotIn("bob", ids)

    def test_production_work_product_is_task_first_interactive_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            case_path = Path(td) / "case.json"
            case_path.write_text(json.dumps(GOLDEN), encoding="utf-8")
            out = Path(td) / "out"
            run_case(case_path, out)
            page = (out / "index.html").read_text(encoding="utf-8")

        self.assertIn("Intelligence Desk", page)
        self.assertIn("Executive answer", page)
        self.assertIn("Ownership map", page)
        self.assertIn("Analyst brief", page)
        self.assertIn("Evidence", page)
        self.assertIn("Click any relationship", page)
        self.assertIn("application/json", page)
        self.assertIn("OWNCTRL-GOLD-001", page)


if __name__ == "__main__":
    unittest.main()
