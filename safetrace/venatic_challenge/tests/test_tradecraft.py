from __future__ import annotations

import json
import unittest
from pathlib import Path

from safetrace.venatic_challenge.hypotheses import build_board
from safetrace.venatic_challenge.run_initial import initial_source_ids
from safetrace.venatic_challenge.source_independence import assess_claim, cluster_sources


BASE = Path(__file__).resolve().parents[1]


class TradecraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case = json.loads((BASE / "case_v002.json").read_text(encoding="utf-8"))

    def test_media_mirror_counts_as_one_independent_origin(self) -> None:
        result = assess_claim(self.case, "Meridian is linked to a sanctioned Petrovic", ["S09", "S27"])
        self.assertEqual(result["reported_source_count"], 2)
        self.assertEqual(result["independent_origin_count"], 1)
        self.assertEqual(result["independent_origins"], ["S09"])
        self.assertTrue(result["corroboration_warning"])

    def test_source_clusters_expose_circular_reporting(self) -> None:
        clusters = {row["origin_source_id"]: row for row in cluster_sources(self.case, ["S09", "S27"])}
        self.assertEqual(clusters["S09"]["source_ids"], ["S09", "S27"])
        self.assertTrue(clusters["S09"]["circular_reporting"])

    def test_initial_hypothesis_board_rejects_sanctions_match(self) -> None:
        board = {row["id"]: row for row in build_board(initial_source_ids(self.case))}
        self.assertEqual(board["H1"]["status"], "rejected")
        self.assertEqual(board["H2"]["status"], "unresolved")
        self.assertEqual(board["H4"]["status"], "unresolved")
        self.assertEqual(board["H6"]["status"], "supported")

    def test_follow_up_evidence_resolves_two_hypotheses_without_closing_nominee_gap(self) -> None:
        available = initial_source_ids(self.case) | {"S25", "S28", "S19", "S22", "S24"}
        board = {row["id"]: row for row in build_board(available)}
        self.assertEqual(board["H2"]["status"], "rejected")
        self.assertEqual(board["H4"]["status"], "rejected")
        self.assertEqual(board["H5"]["status"], "rejected")
        self.assertIn("S12", board["H5"]["disconfirming_evidence"])


if __name__ == "__main__":
    unittest.main()
