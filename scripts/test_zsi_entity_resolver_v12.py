from __future__ import annotations

import unittest

from zsi_entity_resolver_v12 import predict


class EntityResolverV12Tests(unittest.TestCase):
    def decide(self, a: dict, b: dict):
        return predict(a, b)

    def test_dotted_legal_form_merges_with_compatible_address(self):
        decision, _, _ = self.decide(
            {"name": "Nordlicht Energy GmbH", "address": "Hamburg"},
            {"name": "Nordlicht Energy G.m.b.H.", "address": "Hamburg"},
        )
        self.assertEqual(decision, "merge")

    def test_group_and_operating_company_do_not_collapse(self):
        decision, _, _ = self.decide(
            {"name": "DMK GmbH", "address": "Bremen"},
            {"name": "DMK Group", "address": "Bremen"},
        )
        self.assertEqual(decision, "separate")

    def test_group_label_variants_can_merge(self):
        decision, _, _ = self.decide(
            {"name": "Sprehe Unternehmensgruppe", "address": "Cappeln"},
            {"name": "Sprehe Gruppe", "address": "Cappeln"},
        )
        self.assertEqual(decision, "merge")

    def test_same_generic_name_with_conflicting_addresses_stays_separate(self):
        decision, _, _ = self.decide(
            {"name": "Central Services GmbH", "address": "Leipzig"},
            {"name": "Central Services GmbH", "address": "Dresden"},
        )
        self.assertEqual(decision, "separate")

    def test_conflicting_legal_forms_route_to_review(self):
        decision, reason, _ = self.decide(
            {"name": "Aster Data AG", "address": "Zürich"},
            {"name": "Aster Data GmbH", "address": "Zürich"},
        )
        self.assertEqual(decision, "review")
        self.assertIn("legal forms", reason)

    def test_matching_stable_identifiers_override_name_change(self):
        decision, _, _ = self.decide(
            {"name": "Blue Harbor Technologies Ltd", "stable_id": "GB-991122"},
            {"name": "Blue Harbour Systems Limited", "stable_id": "GB-991122"},
        )
        self.assertEqual(decision, "merge")

    def test_conflicting_stable_identifiers_force_separation(self):
        decision, _, _ = self.decide(
            {"name": "Blue Harbor Technologies Ltd", "stable_id": "GB-991122"},
            {"name": "Blue Harbor Technologies Ltd", "stable_id": "GB-887744"},
        )
        self.assertEqual(decision, "separate")

    def test_missing_corroboration_can_abstain(self):
        decision, _, _ = self.decide(
            {"name": "Atlas Infrastructure Partners GmbH", "address": ""},
            {"name": "Atlas Infrastructure Partners", "address": ""},
        )
        self.assertEqual(decision, "review")

    def test_every_decision_returns_an_evidence_contract(self):
        _, _, evidence = self.decide(
            {"name": "Grünwerk Anlagenbau GmbH", "address": "Köln"},
            {"name": "Gruenwerk Anlagenbau", "address": "Köln"},
        )
        for key in (
            "base_a",
            "base_b",
            "legal_form_a",
            "legal_form_b",
            "group_a",
            "group_b",
            "address_relation",
        ):
            self.assertIn(key, evidence)


if __name__ == "__main__":
    unittest.main()
