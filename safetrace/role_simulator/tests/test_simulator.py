from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
DATA_PATH = ROOT / "simulator-data.js"
HTML_PATH = ROOT / "index.html"


def load_data() -> dict:
    raw = DATA_PATH.read_text(encoding="utf-8")
    match = re.fullmatch(
        r"window\.SAFETRACE_SIMULATOR_DATA\s*=\s*(\{.*\})\s*;\s*",
        raw,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError("simulator-data.js must contain one JSON object assignment")
    return json.loads(match.group(1))


class RoleSimulatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = load_data()
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.cases = {case["id"]: case for case in cls.data["cases"]}

    def test_truthful_boundary_is_closed(self) -> None:
        boundary = self.data["boundary"]
        self.assertTrue(boundary["simulationOnly"])
        self.assertTrue(boundary["browserLocalState"])
        self.assertFalse(boundary["productionAuthentication"])
        self.assertFalse(boundary["realPublication"])
        self.assertFalse(boundary["restrictedData"])
        self.assertIn("different evidence classes", boundary["notice"])

    def test_six_roles_and_five_cases_are_available(self) -> None:
        self.assertEqual(
            {role["id"] for role in self.data["roles"]},
            {"citizen", "investigator", "evidence_manager", "reviewer", "legal_reviewer", "publisher"},
        )
        self.assertEqual(set(self.cases), {"case-001", "case-002", "case-003", "case-004", "case-005"})

    def test_no_role_receives_prohibited_capabilities(self) -> None:
        prohibited = {"publish_real", "contact_subject", "refer_authority", "identify_face", "hack", "open_restricted_data"}
        for role in self.data["roles"]:
            self.assertFalse(prohibited.intersection(role["allowedActions"]), role["id"])

    def test_every_case_is_complete_enough_to_explore(self) -> None:
        for case in self.data["cases"]:
            self.assertGreaterEqual(len(case["sources"]), 3, case["id"])
            self.assertGreaterEqual(len(case["claims"]), 3, case["id"])
            self.assertGreaterEqual(len(case["timeline"]), 3, case["id"])
            self.assertGreaterEqual(len(case["graph"]["nodes"]), 4, case["id"])
            self.assertGreaterEqual(len(case["graph"]["edges"]), 3, case["id"])
            self.assertGreaterEqual(len(case["agents"]), 3, case["id"])
            self.assertEqual(set(case["tasks"]), {role["id"] for role in self.data["roles"]})
            for source in case["sources"]:
                self.assertIn(source["zone"], {"public", "synthetic"})
            for claim in case["claims"]:
                self.assertTrue(claim["text"])
                self.assertTrue(claim["limitation"])
                self.assertIn(claim["verdict"], {"supported", "not_supported", "rejected", "partly_supported"})

    def test_only_synthetic_cases_have_training_success_paths(self) -> None:
        publishable = {case["id"] for case in self.data["cases"] if case["publication"]["allowedInSimulation"]}
        blocked = {case["id"] for case in self.data["cases"] if not case["publication"]["allowedInSimulation"]}
        self.assertEqual(publishable, {"case-002", "case-003"})
        self.assertEqual(blocked, {"case-001", "case-004", "case-005"})
        self.assertTrue(all(self.cases[case_id]["kind"] == "synthetic training fixture" for case_id in publishable))

    def test_case_001_overclaim_is_corrected(self) -> None:
        case = self.cases["case-001"]
        self.assertEqual(case["readiness"]["sources"], 3)
        self.assertEqual(case["readiness"]["originals"], 0)
        self.assertFalse(case["publication"]["allowedInSimulation"])
        self.assertTrue(all(source["state"] == "backfill_required" for source in case["sources"]))

    def test_case_004_and_case_005_fail_closed(self) -> None:
        self.assertEqual(self.cases["case-004"]["readiness"]["originals"], 0)
        self.assertEqual(self.cases["case-004"]["readiness"]["sources"], 11)
        case_005 = self.cases["case-005"]
        self.assertEqual(case_005["readiness"]["sources"], 4)
        self.assertEqual(case_005["readiness"]["originals"], 0)
        self.assertEqual(case_005["readiness"]["humanReviewed"], 0)
        self.assertEqual(case_005["status"], "live_acquisition_and_human_review_pending")

    def test_causal_and_stage_boundaries_are_explicit(self) -> None:
        self.assertEqual(next(c for c in self.cases["case-002"]["claims"] if c["id"] == "c2-3")["verdict"], "rejected")
        self.assertEqual(next(c for c in self.cases["case-003"]["claims"] if c["id"] == "c3-3")["verdict"], "rejected")

    def test_html_is_local_accessible_and_resettable(self) -> None:
        required_fragments = (
            'lang="de"', 'aria-label="Hauptnavigation"', 'aria-live="polite"',
            "localStorage", "simulator-data.js", "Fall und Rolle zurücksetzen",
            "Simulation only", "Keine Aktion verändert echte Fälle",
        )
        for fragment in required_fragments:
            self.assertIn(fragment, self.html)
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

    def test_all_declared_views_are_rendered(self) -> None:
        for view in self.data["views"]:
            self.assertRegex(self.html, rf"\b{re.escape(view)}\b")


if __name__ == "__main__":
    unittest.main()
