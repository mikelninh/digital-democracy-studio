from __future__ import annotations

import argparse
import json
from pathlib import Path

from .desk import InvestigationDesk
from .model import (
    DeskCase, DeskComment, DeskDecision, DeskRecord, PublicationRequest,
    SessionContext, TeamTask, plain,
)
from .views import workspace_manifest

NOW = "2026-07-24T11:00:00+00:00"


def session(subject: str, role: str, zone: str = "sensitive_internal") -> SessionContext:
    return SessionContext(
        subject, role, True, "synthetic-ci-identity", f"session:{subject}", zone, NOW,
    )


def build(output_root: Path) -> dict:
    desk = InvestigationDesk()
    intake = session("user:intake", "intake_researcher", "public")
    investigator = session("user:investigator", "investigator")
    reviewer = session("user:reviewer", "reviewer")
    publisher = session("user:publisher", "publisher", "public")
    admin = session("user:admin", "admin")

    case = DeskCase(
        "case:desk-fixture",
        "Synthetic Investigation Desk reference workflow",
        "Can a small team complete a public-source case without bypassing review?",
        "triage",
        investigator.subject_id,
        "public",
        "The fixture tests accountable team workflow and public separation.",
        "Only approved public synthetic claims may leave the internal Desk.",
        NOW,
        NOW,
    )
    desk.create_case(intake, case)
    desk.transition_case(
        investigator, case.id, "accept_case", "2026-07-24T11:01:00+00:00",
        "The bounded public-source question meets the Case Charter boundary.",
    )

    source = DeskRecord(
        "source:desk-fixture", case.id, "source", "Synthetic official record",
        "registered", "public", investigator.subject_id,
        "2026-07-24T11:02:00+00:00",
        {"url": "https://example.org/synthetic-official", "receipt_id": "receipt:synthetic"},
    )
    desk.add_record(investigator, source)

    claim = DeskRecord(
        "claim:desk-fixture", case.id, "claim", "Reviewed synthetic claim",
        "draft", "public", investigator.subject_id,
        "2026-07-24T11:03:00+00:00",
        {
            "text": "The synthetic official record contains the reviewed fixture statement.",
            "evidence_state": "verified_fact",
            "source_anchor": "paragraph 1",
        },
        (source.id,),
    )
    desk.add_record(investigator, claim)

    proposal = DeskRecord(
        "proposal:desk-fixture", case.id, "agent_proposal", "Reader proposal",
        "proposal_ready", "public", investigator.subject_id,
        "2026-07-24T11:04:00+00:00",
        {
            "agent_type": "reader",
            "run_id": "run:synthetic",
            "proposal_only": True,
            "auto_approved": False,
            "source_anchor": "paragraph 1",
        },
        (source.id,),
    )
    desk.add_record(investigator, proposal)
    desk.accept_agent_proposal(
        investigator, proposal.id, "2026-07-24T11:05:00+00:00",
        "The proposal is useful enough to enter human review, not to become a fact.",
    )

    task = TeamTask(
        "task:review-claim", case.id, "Review the fixture claim",
        reviewer.subject_id, "open", investigator.subject_id,
        "2026-07-24T11:06:00+00:00",
    )
    desk.assign_task(investigator, task)
    desk.comment(
        investigator,
        DeskComment(
            "comment:1", case.id, claim.id, investigator.subject_id,
            "Please verify the exact anchor and bounded wording.",
            "2026-07-24T11:07:00+00:00",
        ),
    )
    desk.submit_review(investigator, claim.id, "2026-07-24T11:08:00+00:00")
    desk.decide_review(
        reviewer,
        DeskDecision(
            "decision:claim", case.id, claim.id, "evidence_review", "approved",
            reviewer.subject_id,
            "The public synthetic wording is supported by the exact recorded anchor.",
            "2026-07-24T11:09:00+00:00",
        ),
    )

    publication = PublicationRequest(
        "publication:desk-fixture", case.id, (claim.id,), "draft",
        investigator.subject_id, "2026-07-24T11:10:00+00:00",
    )
    desk.request_publication(investigator, publication)
    desk.approve_publication(
        publisher, publication.id, "2026-07-24T11:11:00+00:00",
        "The claim is public, review-approved and contains no internal-only material.",
    )
    desk.publish(publisher, publication.id, "2026-07-24T11:12:00+00:00")
    public_export = desk.export_public(
        publisher, publication.id, "2026-07-24T11:13:00+00:00",
    )

    prohibited_results = {}
    try:
        desk.approve_publication(
            investigator, publication.id, "2026-07-24T11:14:00+00:00",
            "An investigator should not be allowed to approve publication.",
        )
        prohibited_results["investigator_publish_approval"] = "unexpected_success"
    except (PermissionError, ValueError) as exc:
        prohibited_results["investigator_publish_approval"] = str(exc)

    try:
        unauthenticated = SessionContext(
            "anonymous", "investigator", False, "none", "session:none",
            "public", NOW,
        )
        desk.create_case(unauthenticated, case)
        prohibited_results["unauthenticated_action"] = "unexpected_success"
    except (PermissionError, ValueError) as exc:
        prohibited_results["unauthenticated_action"] = str(exc)

    admin_workspace = workspace_manifest(
        desk, admin, "2026-07-24T11:15:00+00:00",
    )
    publisher_workspace = workspace_manifest(
        desk, publisher, "2026-07-24T11:15:00+00:00",
    )
    audit_verification = desk.verify_audit_chain()

    desk.correct_publication(
        publisher, publication.id, "2026-07-24T11:16:00+00:00",
        "Synthetic correction exercise: publication must become visibly stale.",
    )
    correction_workspace = workspace_manifest(
        desk, admin, "2026-07-24T11:17:00+00:00",
    )
    corrected_audit = desk.verify_audit_chain()

    all_views = set(admin_workspace["views"])
    status = "pass" if (
        len(all_views) == 11
        and public_export["internal_comments_included"] is False
        and public_export["internal_tasks_included"] is False
        and public_export["agent_proposals_included"] is False
        and publication.status == "stale"
        and correction_workspace["views"]["corrections"]["items"]
        and audit_verification["status"] == "pass"
        and corrected_audit["status"] == "pass"
        and "cannot perform approve_publication" in prohibited_results["investigator_publish_approval"]
        and "Authenticated internal session required" in prohibited_results["unauthenticated_action"]
        and admin_workspace["public_portal_is_logically_separate"] is True
        and admin_workspace["chat_is_authoritative"] is False
        and admin_workspace["spreadsheet_is_authoritative"] is False
    ) else "fail"

    result = {
        "schema_version": "safetrace.investigation-desk-release/1.6",
        "status": status,
        "views": {"implemented": sorted(all_views), "count": len(all_views)},
        "roles": {
            "tested": [intake.role, investigator.role, reviewer.role, publisher.role, admin.role],
            "production_identity_provider_configured": False,
            "synthetic_authenticated_sessions": True,
        },
        "workflow": {
            "case_status": case.status,
            "claim_review_state": claim.review_state,
            "agent_proposal_status": proposal.status,
            "publication_status_after_correction": publication.status,
            "public_export": public_export,
        },
        "audit": corrected_audit,
        "prohibited_actions": prohibited_results,
        "workspace": {
            "admin": admin_workspace,
            "publisher": publisher_workspace,
            "after_correction": correction_workspace,
        },
        "boundaries": {
            "authoritative_internal_system": True,
            "public_portal_separate": True,
            "agent_proposals_auto_publish": False,
            "production_auth_ready": False,
            "restricted_partner_data": False,
        },
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "release-report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "public-export.json").write_text(
        json.dumps(public_export, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root", type=Path,
        default=Path("safetrace/investigation_desk/artifacts"),
    )
    args = parser.parse_args()
    result = build(args.output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
