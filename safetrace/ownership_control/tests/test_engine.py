from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from safetrace.ownership_control.engine import investigate, run_case
from safetrace.ownership_control.from_live_company import ownership_case_from_live_company

HERE = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((HERE / "fixtures" / "golden_case.json").read_text(encoding="utf-8"))


def edge(edge_id, owner, target, economic, voting=None, *, status="established", rights=None, source="s"):
    return {
        "id": edge_id, "owner_id": owner, "target_id": target,
        "economic_pct": economic, "voting_pct": voting, "status": status,
        "control_rights": rights or [],
        "evidence": [{"source_id": source, "anchor": f"anchor-{edge_id}"}] if status == "established" else [],
    }


def base_case():
    return {
        "case_id": "TEST", "classification": "SYNTHETIC TEST", "target_entity_id": "t",
        "policy": {"ubo_threshold": 0.25, "ubo_threshold_operator": "gt"},
        "sources": [{"id": "s", "title": "Synthetic evidence"}],
        "entities": [
            {"id": "t", "name": "Target", "kind": "company", "resolution_status": "confirmed"},
            {"id": "h", "name": "Holding", "kind": "company", "resolution_status": "confirmed"},
            {"id": "a", "name": "Alice", "kind": "person", "resolution_status": "confirmed"},
            {"id": "b", "name": "Bob", "kind": "person", "resolution_status": "confirmed"},
        ],
        "ownership_edges": [], "collection_gaps": [],
    }


class OwnershipControlTests(unittest.TestCase):
    def test_indirect_60_times_70_equals_42_percent(self):
        case = base_case()
        case["ownership_edges"] = [edge("h-t", "h", "t", 0.70, 0.80), edge("a-h", "a", "h", 0.60, 0.55)]
        result = investigate(case)
        alice = next(x for x in result["economic_ownership"] if x["owner_id"] == "a")
        self.assertAlmostEqual(alice["aggregate_pct"], 0.42)
        self.assertEqual(alice["path_count"], 1)

    def test_multiple_paths_are_summed(self):
        result = investigate(copy.deepcopy(GOLDEN))
        alice = next(x for x in result["economic_ownership"] if x["owner_id"] == "alice")
        self.assertAlmostEqual(alice["aggregate_pct"], 0.48)
        self.assertEqual(alice["path_count"], 2)

    def test_voting_is_separate_from_equity(self):
        result = investigate(copy.deepcopy(GOLDEN))
        alice_e = next(x for x in result["economic_ownership"] if x["owner_id"] == "alice")
        alice_v = next(x for x in result["voting_rights"] if x["owner_id"] == "alice")
        self.assertAlmostEqual(alice_e["aggregate_pct"], 0.48)
        self.assertAlmostEqual(alice_v["aggregate_pct"], 0.50)
        self.assertNotEqual(alice_e["aggregate_pct"], alice_v["aggregate_pct"])

    def test_missing_intermediate_percentage_blocks_downstream_ubo(self):
        case = base_case()
        case["ownership_edges"] = [edge("h-t", "h", "t", None, 0.80), edge("a-h", "a", "h", 0.60, 0.55)]
        result = investigate(case)
        self.assertFalse(any(x["entity_id"] == "a" and "economic_ownership_threshold" in x["grounds"] for x in result["ubo_candidates"]))
        self.assertTrue(any(x.get("status") == "blocked_missing_economic_pct" for x in result["unresolved"]))

    def test_cycle_is_detected_and_not_infinitely_propagated(self):
        case = base_case()
        case["ownership_edges"] = [edge("h-t", "h", "t", 0.70, 0.70), edge("a-h", "a", "h", 0.60, 0.60), edge("h-a", "h", "a", 0.10, 0.10)]
        result = investigate(case)
        self.assertGreaterEqual(result["metrics"]["cycles"], 1)
        self.assertTrue(any(x.get("type") == "ownership_cycle" for x in result["unresolved"]))
        self.assertLess(result["metrics"]["economic_paths"], 20)

    def test_ambiguous_identity_blocks_propagation(self):
        case = base_case()
        next(x for x in case["entities"] if x["id"] == "a")["resolution_status"] = "ambiguous"
        case["ownership_edges"] = [edge("h-t", "h", "t", 0.70, 0.70), edge("a-h", "a", "h", 0.60, 0.60)]
        result = investigate(case)
        self.assertFalse(any(x["owner_id"] == "a" for x in result["economic_ownership"]))
        self.assertTrue(any(x.get("status") == "blocked_identity_ambiguous" for x in result["unresolved"]))

    def test_explicit_control_right_can_create_candidate_below_equity_threshold(self):
        case = base_case()
        case["ownership_edges"] = [edge("a-t", "a", "t", 0.05, 0.05, rights=["board_appointment"])]
        result = investigate(case)
        candidate = next(x for x in result["ubo_candidates"] if x["entity_id"] == "a")
        self.assertIn("documented_control_right", candidate["grounds"])
        self.assertNotIn("economic_ownership_threshold", candidate["grounds"])

    def test_threshold_is_configurable(self):
        case = base_case()
        case["ownership_edges"] = [edge("a-t", "a", "t", 0.25, 0.25)]
        gt = investigate(copy.deepcopy(case))
        self.assertFalse(any(x["entity_id"] == "a" for x in gt["ubo_candidates"]))
        case["policy"]["ubo_threshold_operator"] = "gte"
        gte = investigate(case)
        self.assertTrue(any(x["entity_id"] == "a" for x in gte["ubo_candidates"]))

    def test_missing_ownership_is_not_inferred(self):
        case = base_case()
        case["collection_gaps"] = [{"type": "shareholder_list_missing", "reason": "No authoritative shareholder list was acquired."}]
        result = investigate(case)
        self.assertEqual(result["economic_ownership"], [])
        self.assertEqual(result["ubo_candidates"], [])
        self.assertFalse(result["decision_boundary"]["ownership_established"])
        self.assertTrue(any(x.get("type") == "shareholder_list_missing" for x in result["unresolved"]))

    def test_every_propagated_path_has_evidence_why_chain(self):
        result = investigate(copy.deepcopy(GOLDEN))
        for owner in result["economic_ownership"]:
            for path in owner["paths"]:
                self.assertTrue(path["edge_ids"])
                self.assertEqual(len(path["edge_ids"]), len(path["evidence"]))
                self.assertTrue(all(ev.get("source_id") and ev.get("anchor") for ev in path["evidence"]))

    def test_live_company_boundary_does_not_fabricate_shareholders(self):
        live = {
            "schema_version": "safetrace.live-company-investigation/2.2",
            "case": {"id": "LIVE-VENATIC-001", "title": "Venatic Intelligence GmbH"},
            "claims": [{"field": "legal_name", "value": "Venatic Intelligence GmbH"}, {"field": "register_id", "value": "HRB 285675"}],
            "sources": [{"id": "venatic-official", "title": "Official", "publisher": "Venatic", "acquisition_status": "acquired", "sha256": "abc", "receipt_hash": "def", "resolved_url": "https://example.test"}],
            "unresolved_questions": [{"field": "shareholders", "title": "Shareholder and beneficial-ownership chain", "reason": "Not established by reviewed live evidence.", "next_step": "Obtain the current Gesellschafterliste."}],
        }
        case = ownership_case_from_live_company(live)
        self.assertEqual(case["ownership_edges"], [])
        self.assertEqual(len(case["collection_gaps"]), 1)
        result = investigate(case)
        self.assertEqual(result["ubo_candidates"], [])
        self.assertFalse(result["decision_boundary"]["ownership_established"])

    def test_golden_case_outputs_json_markdown_and_html(self):
        with tempfile.TemporaryDirectory() as td:
            case_path = Path(td) / "case.json"
            case_path.write_text(json.dumps(GOLDEN), encoding="utf-8")
            out = Path(td) / "out"
            result = run_case(case_path, out)
            self.assertEqual(result["schema_version"], "safetrace.ownership-control/1.0")
            self.assertTrue((out / "result.json").exists())
            self.assertIn("Show me why", (out / "index.html").read_text(encoding="utf-8"))
            self.assertIn("UBO candidates", (out / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
