from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from safetrace.review_desk.evaluate import evaluate
from safetrace.review_desk.model import Claim, Decision, EvidenceRef


SOURCE = EvidenceRef(
    id="evidence:one",
    role="supporting",
    source_id="official-source",
    source_url="https://example.test/official",
    source_title="Official source",
    summary="The official source supports the claim.",
)


class ReviewDeskTests(unittest.TestCase):
    def test_claim_without_human_decision_is_blocked(self) -> None:
        claim = Claim(
            id="claim:one",
            text="A fact",
            evidence_state="verified_fact",
            sensitivity="ordinary",
            origin="ai_suggested",
            evidence=[SOURCE],
        )
        publishable, blockers = claim.publication_check()
        self.assertFalse(publishable)
        self.assertIn("missing_human_decision", blockers)

    def test_sensitive_claim_requires_legal_review_and_reply(self) -> None:
        claim = Claim(
            id="claim:sensitive",
            text="A sensitive allegation",
            evidence_state="official_allegation",
            sensitivity="sensitive",
            origin="human",
            evidence=[SOURCE],
            decision=Decision(
                outcome="approved",
                reviewer_role="editor",
                rationale="Evidence reviewed.",
                decided_at="2026-07-23T20:00:00Z",
                legal_review="pending",
                right_of_reply="pending",
            ),
        )
        publishable, blockers = claim.publication_check()
        self.assertFalse(publishable)
        self.assertIn("sensitive_claim_requires_legal_review", blockers)
        self.assertIn("sensitive_claim_requires_right_of_reply", blockers)

    def test_reviewed_queue_publishes_only_two_verified_claims(self) -> None:
        queue = Path(__file__).parents[1] / "data/claims.json"
        with tempfile.TemporaryDirectory() as directory:
            public, report = evaluate(
                queue,
                Path(directory) / "public.json",
                Path(directory) / "review.json",
            )
        self.assertEqual(report["summary"], {"total": 3, "publishable": 2, "blocked": 1})
        self.assertEqual(len(public["claims"]), 2)
        self.assertTrue(all(item["evidence_state"] == "verified_fact" for item in public["claims"]))
        blocked = [item for item in report["claims"] if not item["publication"]["publishable"]]
        self.assertEqual(blocked[0]["decision"]["outcome"], "rejected")


if __name__ == "__main__":
    unittest.main()
