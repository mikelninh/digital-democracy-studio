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

    def test_truthful_boundary_is_closed(self) -> None:
        boundary = self.data["boundary"]
        self.assertTrue(boundary["simulationOnly"])
        self.assertTrue(boundary["browserLocalState"])
        self.assertFalse(boundary["productionAuthentication"])
        self.assertFalse(boundary["realPublication"])
        self.assertFalse(boundary["restrictedData"])

    def test_six_roles_and_four_existing_cases_are_available(self) -> None:
        self.assertEqual(
            {role["id"] for role in self.data["roles"]},
            {
                "citizen",
                "investigator",
                "evidence_manager",
                "reviewer",
                "legal_reviewer",
                "publisher",
            },
        )
        self.assertEqual(
            {case["id"] for case in self.data["cases"]},
            {"case-001", "case-002", "case-003", "case-004"},
        )

    def test_no_role_receives_prohibited_capabilities(self) -> None:
        prohibited = {
            "publish_real",
            "contact_subject",
            "refer_authority",
            "identify_face",
            "hack",
            "open_restricted_data",
        }
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
                self.assertIn(
                    claim["verdict"],
                    {"supported", "not_supported", "rejected", "partly_supported"},
                )

    def test_simulator_contains_success_and_fail_closed_publication_paths(self) -> None:
        publishable = [case for case in self.data["cases"] if case["publication"]["allowedInSimulation"]]
        blocked = [case for case in self.data["cases"] if not case["publication"]["allowedInSimulation"]]
        self.assertGreaterEqual(len(publishable), 1)
        self.assertEqual([case["id"] for case in blocked], ["case-004"])
        self.assertEqual(blocked[0]["readiness"]["originals"], 0)
        self.assertEqual(blocked[0]["readiness"]["sources"], 11)

    def test_causal_and_stage_boundaries_are_explicit(self) -> None:
        money = next(case for case in self.data["cases"] if case["id"] == "case-002")
        arms = next(case for case in self.data["cases"] if case["id"] == "case-003")
        self.assertEqual(next(c for c in money["claims"] if c["id"] == "c2-3")["verdict"], "rejected")
        self.assertEqual(next(c for c in arms["claims"] if c["id"] == "c3-3")["verdict"], "rejected")

    def test_html_is_local_accessible_and_resettable(self) -> None:
        required_fragments = (
            'lang="de"',
            'aria-label="Hauptnavigation"',
            'aria-live="polite"',
            'localStorage',
            'simulator-data.js',
            'Fall und Rolle zurücksetzen',
            'Simulation only',
            'Keine Aktion verändert echte Fälle',
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
