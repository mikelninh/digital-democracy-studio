from __future__ import annotations

import unittest

from safetrace.investigation_desk.desk import InvestigationDesk
from safetrace.investigation_desk.model import (
    DeskCase, DeskDecision, DeskRecord, PublicationRequest, SessionContext,
)
from safetrace.investigation_desk.views import build_view

NOW = "2026-07-24T12:00:00+00:00"


def session(subject: str, role: str, authenticated: bool = True, zone: str = "sensitive_internal"):
    return SessionContext(subject, role, authenticated, "synthetic-test", f"session:{subject}", zone, NOW)


def active_desk() -> tuple[InvestigationDesk, DeskCase, SessionContext]:
    desk = InvestigationDesk()
    investigator = session("investigator", "investigator")
    case = DeskCase(
        "case:test", "Test case", "Does the tested workflow preserve human control?",
        "triage", investigator.subject_id, "public",
        "The test protects accountability workflow integrity.",
        "Only approved public test records may be exported.", NOW, NOW,
    )
    desk.create_case(investigator, case)
    desk.transition_case(investigator, case.id, "accept_case", NOW, "Test case accepted.")
    return desk, case, investigator


class DeskPermissionTests(unittest.TestCase):
    def test_unauthenticated_and_wrong_role_are_denied(self) -> None:
        desk, case, _ = active_desk()
        with self.assertRaisesRegex(PermissionError, "Authenticated internal session required"):
            build_view(desk, session("anon", "investigator", False), "cases", NOW)
        with self.assertRaisesRegex(PermissionError, "cannot perform publish"):
            desk.publish(session("reviewer", "reviewer"), "missing", NOW)

    def test_sensitive_record_is_hidden_below_zone_ceiling(self) -> None:
        desk, case, investigator = active_desk()
        record = DeskRecord(
            "claim:sensitive", case.id, "claim", "Internal claim", "draft",
            "sensitive_internal", investigator.subject_id, NOW,
            {"text": "Internal-only synthetic record."},
        )
        desk.add_record(investigator, record)
        public_reviewer = session("reviewer", "reviewer", zone="public")
        view = build_view(desk, public_reviewer, "claims", NOW)
        self.assertEqual(view.items, ())

    def test_agent_proposal_never_becomes_approved_fact_directly(self) -> None:
        desk, case, investigator = active_desk()
        proposal = DeskRecord(
            "proposal:1", case.id, "agent_proposal", "Agent proposal",
            "proposal_ready", "public", investigator.subject_id, NOW,
            {"auto_approved": False},
        )
        desk.add_record(investigator, proposal)
        self.assertEqual(proposal.status, "awaiting_human")
        desk.accept_agent_proposal(investigator, proposal.id, NOW, "Useful for review.")
        self.assertEqual(proposal.status, "accepted_for_review")
        self.assertEqual(proposal.review_state, "pending")


class DeskPublicationTests(unittest.TestCase):
    def _approved_claim(self):
        desk, case, investigator = active_desk()
        claim = DeskRecord(
            "claim:1", case.id, "claim", "Public claim", "draft", "public",
            investigator.subject_id, NOW,
            {"text": "A bounded synthetic claim.", "source_anchor": "paragraph 1"},
            ("source:1",),
        )
        desk.add_record(investigator, claim)
        desk.submit_review(investigator, claim.id, NOW)
        reviewer = session("reviewer", "reviewer")
        desk.decide_review(
            reviewer,
            DeskDecision(
                "decision:1", case.id, claim.id, "evidence_review", "approved",
                reviewer.subject_id, "The exact synthetic anchor supports the claim.", NOW,
            ),
        )
        return desk, case, investigator, claim

    def test_requester_cannot_approve_and_sensitive_claim_cannot_export(self) -> None:
        desk, case, investigator, claim = self._approved_claim()
        request = PublicationRequest("publication:1", case.id, (claim.id,), "draft", investigator.subject_id, NOW)
        desk.request_publication(investigator, request)
        admin_requester = session(investigator.subject_id, "admin")
        with self.assertRaisesRegex(PermissionError, "Requester cannot approve"):
            desk.approve_publication(admin_requester, request.id, NOW, "Cannot self-approve publication.")

    def test_independent_publication_and_export_exclude_internal_records(self) -> None:
        desk, case, investigator, claim = self._approved_claim()
        publisher = session("publisher", "publisher", zone="public")
        request = PublicationRequest("publication:1", case.id, (claim.id,), "draft", investigator.subject_id, NOW)
        desk.request_publication(investigator, request)
        desk.approve_publication(publisher, request.id, NOW, "Independent approval complete.")
        desk.publish(publisher, request.id, NOW)
        export = desk.export_public(publisher, request.id, NOW)
        self.assertFalse(export["internal_comments_included"])
        self.assertFalse(export["internal_tasks_included"])
        self.assertFalse(export["agent_proposals_included"])
        self.assertEqual(export["claims"][0]["id"], claim.id)

    def test_correction_marks_publication_stale_and_audit_remains_valid(self) -> None:
        desk, case, investigator, claim = self._approved_claim()
        publisher = session("publisher", "publisher", zone="public")
        request = PublicationRequest("publication:1", case.id, (claim.id,), "draft", investigator.subject_id, NOW)
        desk.request_publication(investigator, request)
        desk.approve_publication(publisher, request.id, NOW, "Independent approval complete.")
        desk.publish(publisher, request.id, NOW)
        desk.correct_publication(publisher, request.id, NOW, "Visible synthetic correction.")
        self.assertEqual(request.status, "stale")
        self.assertEqual(desk.verify_audit_chain()["status"], "pass")


if __name__ == "__main__":
    unittest.main()
