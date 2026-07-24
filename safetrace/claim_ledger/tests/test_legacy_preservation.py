from __future__ import annotations

import unittest

from safetrace.claim_ledger.ledger import ClaimLedger
from safetrace.claim_ledger.model import ClaimVersion, EvidenceLink, LedgerClaim

NOW = "2026-07-24T07:00:00+00:00"


class LegacyPreservationTests(unittest.TestCase):
    def test_non_material_rejected_claim_is_preserved_but_not_publishable(self) -> None:
        link = EvidenceLink(
            id="legacy-link:rejected:context",
            claim_id="claim:rejected-causation",
            version=1,
            role="context",
            provenance_mode="legacy_reference",
            source_id="source:official-register",
            anchor="Legacy review record",
            summary="The source documents association but does not support the rejected causal allegation.",
            added_by="safetrace-v1.4-migration",
            added_at=NOW,
            legacy_url="https://example.org/official-register",
        )
        version = ClaimVersion(
            claim_id="claim:rejected-causation",
            version=1,
            text="The payment purchased a favourable policy outcome.",
            evidence_state="analytical_red_flag",
            legal_status="not_applicable",
            sensitivity="internal",
            created_by="safetrace-v1.4-migration",
            created_at=NOW,
            evidence_links=(link,),
            limitations=("Rejected because no evidence establishes causation.",),
        )
        claim = LedgerClaim(
            id=version.claim_id,
            case_id="case-002",
            researcher_id="safetrace-v1.4-migration",
            material=False,
            status="migrated_pending_evidence_backfill",
            current_version=1,
            created_at=NOW,
            updated_at=NOW,
            versions={1: version},
        )
        ledger = ClaimLedger()
        ledger.add_claim(claim)

        result = ledger.evaluate(claim.id)

        self.assertFalse(result.ready)
        self.assertIn("Claim version requires supporting evidence", result.blockers)
        self.assertIn("Claim evidence is not fully backed by Evidence Vault receipts", result.blockers)
        self.assertEqual(claim.status, "migrated_pending_evidence_backfill")


if __name__ == "__main__":
    unittest.main()
