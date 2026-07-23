from __future__ import annotations

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from safetrace.political_money.build_graph import build
from safetrace.political_money.model import Edge, Graph, Node


class PoliticalMoneyGraphTests(unittest.TestCase):
    def test_seed_builds_provenance_first_graph(self) -> None:
        seed = Path(__file__).parents[1] / "data/seed.json"
        with tempfile.TemporaryDirectory() as directory:
            payload = build(seed, Path(directory) / "graph.json")
        self.assertEqual(payload["metadata"]["donation_count"], 5)
        self.assertEqual(payload["metadata"]["party_count"], 4)
        self.assertEqual(Decimal(payload["metadata"]["donation_total_eur"]), Decimal("340000.00"))
        donation_edges = [edge for edge in payload["edges"] if edge["type"] == "donated_to"]
        self.assertEqual(len(donation_edges), 5)
        self.assertTrue(all(edge["provenance"] for edge in donation_edges))
        self.assertTrue(all(edge["interpretation"] == "documented_relationship_only" for edge in donation_edges))

    def test_edge_without_provenance_is_rejected(self) -> None:
        graph = Graph(
            nodes=[
                Node(id="org:x", type="organisation", label="X"),
                Node(id="party:y", type="political_party", label="Y"),
            ],
            edges=[
                Edge(
                    id="edge:test",
                    type="donated_to",
                    source="org:x",
                    target="party:y",
                    attributes={"amount_eur": "1", "received_date": "2026-01-01"},
                )
            ],
            metadata={},
        )
        with self.assertRaises(ValueError):
            graph.validate()


if __name__ == "__main__":
    unittest.main()
