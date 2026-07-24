from __future__ import annotations

import unittest
from pathlib import Path

from safetrace.claim_ledger.ledger import ClaimLedger, required_gates
from safetrace.claim_ledger.migration import build_migration_report
from safetrace.claim_ledger.model import (
    ClaimVersion,
    EvidenceLink,
    LedgerClaim,
    LedgerPublication,
    VaultEvidenceRef,
)

NOW = "2026-07-24T06:00:00+00:00"


def make_ledger(*, provenance_mode="vault_receipt", sensitivity="public", contradict=False, metadata=None):
    reference = VaultEvidenceRef("receipt:fixture", "source:fixture", "a" * 64)
    links = [
        EvidenceLink(
            "link:supporting",
            "claim:fixture",
            1,
            "supporting",
            provenance_mode,
            "source:fixture",
            "page 1",
            "The source supports the bounded statement.",
            "researcher",
            NOW,
            "receipt:fixture" if provenance_mode == "vault_receipt" else None,
            "a" * 64 if provenance_mode == "vault_receipt" else None,
            "https://example.org/legacy" if provenance_mode == "legacy_reference" else None,
        )
    ]
    if contradict:
        links.append(
            EvidenceLink(
                "link:contradicting",
                "claim:fixture",
                1,
                "contradicting",
                provenance_mode,
                "source:fixture",
                "page 2",
                "The source also contains a material qualification.",
                "researcher",
                NOW,
                "receipt:fixture" if provenance_mode == "vault_receipt" else None,
                "a" * 64 if provenance_mode == "vault_receipt" else None,
                "https://example.org/legacy" if provenance_mode == "legacy_reference" else None,
            )
        )
    version = ClaimVersion(
        "claim:fixture",
        1,
        "The official source documents the bounded public decision.",
        "verified_fact",
        "not_applicable",
        sensitivity,
        "researcher",
        NOW,
        tuple(links),
        metadata=metadata or {},
    )
    claim = LedgerClaim(
        "claim:fixture",
        "case:fixture",
        "researcher",
        True,
        "draft",
        1,
        NOW,
        NOW,
        {1: version},
    )
    return ClaimLedger({"receipt:fixture": reference}), claim


def approve(ledger: ClaimLedger, claim: LedgerClaim, *, address_contradictions=True, reviewer="reviewer"):
    ledger.add_claim(claim)
    all_gates = ["identity", "evidence", "red_team", "legal", "right_of_reply", "publication", "correction"]
    tasks = ledger.queue_reviews(claim.id, {gate: reviewer for gate in all_gates}, NOW)
    for task in tasks:
        ledger.decide(
            task.id,
            reviewer,
            "approved",
            "Reviewed against the exact source anchors and documented limitations.",
            NOW,
            contradictory_evidence_addressed=address_contradictions and task.gate == "red_team",
        )
    return tasks


class ClaimGateTests(unittest.TestCase):
    def test_vault_backed_claim_can_publish_after_all_gates(self):
        ledger, claim = make_ledger()
        tasks = approve(ledger, claim)
        self.assertEqual({task.gate for task in tasks}, {"evidence", "red_team", "publication"})
        self.assertTrue(ledger.evaluate(claim.id).ready)
        publication = LedgerPublication("publication:1", claim.case_id, ((claim.id, 1),), "draft", NOW, NOW)
        ledger.publish(publication)
        self.assertEqual(publication.status, "published")

    def test_legacy_evidence_is_preserved_but_blocks_publication(self):
        ledger, claim = make_ledger(provenance_mode="legacy_reference")
        approve(ledger, claim)
        result = ledger.evaluate(claim.id)
        self.assertFalse(result.ready)
        self.assertTrue(any("Evidence Vault" in blocker for blocker in result.blockers))

    def test_contradicting_evidence_requires_red_team_acknowledgement(self):
        ledger, claim = make_ledger(contradict=True)
        approve(ledger, claim, address_contradictions=False)
        result = ledger.evaluate(claim.id)
        self.assertFalse(result.ready)
        self.assertIn("Contradicting evidence was not addressed by red-team review", result.blockers)

    def test_sensitive_claim_requires_independent_reviewers(self):
        ledger, claim = make_ledger(sensitivity="internal")
        approve(ledger, claim, reviewer="researcher")
        result = ledger.evaluate(claim.id)
        self.assertFalse(result.ready)
        self.assertTrue(any("reviewer separation" in blocker for blocker in result.blockers))
        self.assertIn("legal", required_gates(claim.versions[1], claim.material))
        self.assertIn("right_of_reply", required_gates(claim.versions[1], claim.material))

    def test_person_claim_adds_identity_legal_and_reply_gates(self):
        ledger, claim = make_ledger(metadata={"identity_sensitive": True, "materially_discusses_person": True})
        gates = required_gates(claim.versions[1], claim.material)
        self.assertEqual(set(gates), {"identity", "evidence", "red_team", "legal", "right_of_reply", "publication"})

    def test_correction_invalidates_old_publication_and_requires_new_reviews(self):
        ledger, claim = make_ledger()
        approve(ledger, claim)
        publication = LedgerPublication("publication:1", claim.case_id, ((claim.id, 1),), "draft", NOW, NOW)
        ledger.publish(publication)
        link = EvidenceLink(
            "link:v2",
            claim.id,
            2,
            "supporting",
            "vault_receipt",
            "source:fixture",
            "page 3",
            "The corrected wording follows the exact reviewed record.",
            "researcher",
            "2026-07-24T06:30:00+00:00",
            "receipt:fixture",
            "a" * 64,
        )
        version = ClaimVersion(
            claim.id,
            2,
            "The reviewed source documents the corrected bounded decision.",
            "verified_fact",
            "not_applicable",
            "public",
            "researcher",
            "2026-07-24T06:30:00+00:00",
            (link,),
            supersedes_version=1,
        )
        correction = ledger.correct(
            claim.id,
            version,
            "factual",
            "The source required a visible factual correction to the published wording.",
            "editor",
            "2026-07-24T06:30:00+00:00",
        )
        self.assertEqual(publication.status, "stale")
        self.assertEqual(correction.invalidated_publication_ids, (publication.id,))
        self.assertFalse(ledger.evaluate(claim.id).ready)
        self.assertIn("correction", required_gates(version, claim.material))


class ExistingCaseMigrationTests(unittest.TestCase):
    def test_all_existing_cases_migrate_without_automatic_publication(self):
        root = Path(__file__).parents[2]
        if not (root / "core").exists() or not (root / "source_engine").exists():
            self.skipTest("Existing SafeTrace cases are not available")
        report = build_migration_report(root)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(set(report["cases"]), {"case-001", "case-002", "case-003", "case-004"})
        self.assertGreater(report["total_claims_imported"], 0)
        self.assertEqual(report["automatic_publications"], 0)
        for case in report["cases"].values():
            self.assertEqual(case["claims_imported"], case["claims_blocked_pending_vault_backfill"])


if __name__ == "__main__":
    unittest.main()
