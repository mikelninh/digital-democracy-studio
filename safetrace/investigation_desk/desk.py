from __future__ import annotations

from dataclasses import replace
from typing import Any

from .model import (
    AuditEvent, DeskCase, DeskComment, DeskDecision, DeskRecord,
    PublicationRequest, SessionContext, TeamTask, canonical, digest, plain,
)
from .policy import require_action, require_zone


class InvestigationDesk:
    def __init__(self) -> None:
        self.cases: dict[str, DeskCase] = {}
        self.records: dict[str, DeskRecord] = {}
        self.tasks: dict[str, TeamTask] = {}
        self.comments: dict[str, DeskComment] = {}
        self.decisions: dict[str, DeskDecision] = {}
        self.publications: dict[str, PublicationRequest] = {}
        self.audit: list[AuditEvent] = []

    def _audit(
        self,
        session: SessionContext,
        action: str,
        case_id: str,
        subject_id: str,
        outcome: str,
        occurred_at: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        previous_hash = self.audit[-1].event_hash if self.audit else None
        sequence = len(self.audit) + 1
        body = {
            "sequence": sequence,
            "case_id": case_id,
            "actor_id": session.subject_id,
            "action": action,
            "subject_id": subject_id,
            "outcome": outcome,
            "occurred_at": occurred_at,
            "previous_hash": previous_hash,
            "details": details or {},
        }
        event_hash = digest(body)
        event = AuditEvent(
            f"audit:{sequence:06d}", sequence, case_id, session.subject_id,
            action, subject_id, outcome, occurred_at, previous_hash,
            event_hash, details or {},
        )
        self.audit.append(event)
        return event

    def _case(self, case_id: str) -> DeskCase:
        if case_id not in self.cases:
            raise KeyError(f"Unknown case: {case_id}")
        return self.cases[case_id]

    def create_case(self, session: SessionContext, case: DeskCase) -> DeskCase:
        require_action(session, "create_case")
        case.validate()
        require_zone(session, case.data_zone)
        if case.id in self.cases:
            raise ValueError("Case already exists")
        if case.status not in {"draft", "triage"}:
            raise ValueError("New case must start as draft or triage")
        self.cases[case.id] = case
        self._audit(session, "create_case", case.id, case.id, "success", case.created_at)
        return case

    def transition_case(
        self,
        session: SessionContext,
        case_id: str,
        action: str,
        occurred_at: str,
        rationale: str,
    ) -> DeskCase:
        require_action(session, action)
        case = self._case(case_id)
        transitions = {
            "accept_case": ({"draft", "triage", "paused"}, "active"),
            "reject_case": ({"draft", "triage"}, "rejected"),
            "pause_case": ({"active"}, "paused"),
            "close_case": ({"active", "paused"}, "closed"),
        }
        if action not in transitions:
            raise ValueError("Unsupported case transition")
        allowed, target = transitions[action]
        if case.status not in allowed:
            raise ValueError(f"Cannot {action} from {case.status}")
        case.status = target
        case.updated_at = occurred_at
        self._audit(
            session, action, case_id, case_id, "success", occurred_at,
            {"rationale": rationale, "new_status": target},
        )
        return case

    def add_record(
        self,
        session: SessionContext,
        record: DeskRecord,
    ) -> DeskRecord:
        action = {
            "source": "add_source", "claim": "add_claim", "entity": "add_entity",
            "relationship": "add_relationship", "event": "add_event",
            "agent_proposal": "queue_agent_proposal",
        }[record.kind]
        require_action(session, action)
        record.validate()
        case = self._case(record.case_id)
        if case.status != "active":
            raise ValueError("Records may only be added to an active case")
        require_zone(session, record.data_zone)
        if record.id in self.records:
            raise ValueError("Record already exists")
        if record.kind == "agent_proposal":
            record.status = "awaiting_human"
            record.review_state = "pending"
            if record.payload.get("auto_approved") is True:
                raise ValueError("Agent proposal cannot be auto-approved")
        self.records[record.id] = record
        self._audit(
            session, action, record.case_id, record.id, "success",
            record.created_at, {"kind": record.kind},
        )
        return record

    def accept_agent_proposal(
        self,
        session: SessionContext,
        record_id: str,
        decided_at: str,
        rationale: str,
    ) -> DeskRecord:
        require_action(session, "accept_agent_proposal_for_review")
        record = self.records[record_id]
        if record.kind != "agent_proposal":
            raise ValueError("Record is not an agent proposal")
        if record.status != "awaiting_human":
            raise ValueError("Agent proposal is not awaiting human review")
        record.status = "accepted_for_review"
        record.review_state = "pending"
        self._audit(
            session, "accept_agent_proposal_for_review", record.case_id,
            record.id, "success", decided_at, {"rationale": rationale},
        )
        return record

    def reject_agent_proposal(
        self,
        session: SessionContext,
        record_id: str,
        decided_at: str,
        rationale: str,
    ) -> DeskRecord:
        require_action(session, "reject_agent_proposal")
        record = self.records[record_id]
        if record.kind != "agent_proposal":
            raise ValueError("Record is not an agent proposal")
        record.status = "rejected"
        record.review_state = "rejected"
        self._audit(
            session, "reject_agent_proposal", record.case_id, record.id,
            "success", decided_at, {"rationale": rationale},
        )
        return record

    def assign_task(self, session: SessionContext, task: TeamTask) -> TeamTask:
        require_action(session, "assign_task")
        task.validate()
        self._case(task.case_id)
        if task.id in self.tasks:
            raise ValueError("Task already exists")
        self.tasks[task.id] = task
        self._audit(
            session, "assign_task", task.case_id, task.id, "success",
            task.created_at, {"assignee": task.assignee_id},
        )
        return task

    def comment(self, session: SessionContext, comment: DeskComment) -> DeskComment:
        require_action(session, "comment")
        comment.validate()
        self._case(comment.case_id)
        if comment.id in self.comments:
            raise ValueError("Comment already exists")
        self.comments[comment.id] = comment
        self._audit(
            session, "comment", comment.case_id, comment.subject_id,
            "success", comment.created_at, {"comment_id": comment.id},
        )
        return comment

    def submit_review(
        self,
        session: SessionContext,
        record_id: str,
        submitted_at: str,
    ) -> DeskRecord:
        require_action(session, "submit_review")
        record = self.records[record_id]
        if record.kind not in {"claim", "relationship", "event", "agent_proposal"}:
            raise ValueError("Record kind cannot enter review")
        if record.review_state not in {"draft", "needs_changes", "pending"}:
            raise ValueError("Record is not reviewable")
        record.review_state = "pending"
        record.status = "in_review"
        self._audit(
            session, "submit_review", record.case_id, record.id,
            "success", submitted_at,
        )
        return record

    def decide_review(
        self,
        session: SessionContext,
        decision: DeskDecision,
    ) -> DeskDecision:
        require_action(session, "decide_review")
        decision.validate()
        record = self.records[decision.subject_id]
        if record.case_id != decision.case_id:
            raise ValueError("Decision crosses case boundary")
        if record.created_by == session.subject_id:
            raise PermissionError("Record creator cannot perform final review")
        if record.review_state != "pending":
            raise ValueError("Record is not pending review")
        if decision.outcome not in {"approved", "rejected", "needs_changes"}:
            raise ValueError("Unsupported review outcome")
        record.review_state = decision.outcome
        record.status = decision.outcome
        self.decisions[decision.id] = decision
        self._audit(
            session, "decide_review", decision.case_id, decision.subject_id,
            decision.outcome, decision.decided_at,
            {"decision_id": decision.id, "rationale": decision.rationale},
        )
        return decision

    def request_publication(
        self,
        session: SessionContext,
        request: PublicationRequest,
    ) -> PublicationRequest:
        require_action(session, "request_publication")
        request.validate()
        case = self._case(request.case_id)
        if case.status != "active":
            raise ValueError("Only active cases can request publication")
        for claim_id in request.claim_ids:
            claim = self.records.get(claim_id)
            if not claim or claim.kind != "claim":
                raise ValueError(f"Unknown publication claim: {claim_id}")
            if claim.review_state != "approved":
                raise ValueError(f"Claim is not review-approved: {claim_id}")
            if claim.data_zone != "public":
                raise ValueError("Sensitive-internal claim cannot enter public request")
        request.status = "requested"
        self.publications[request.id] = request
        self._audit(
            session, "request_publication", request.case_id, request.id,
            "success", request.requested_at,
        )
        return request

    def approve_publication(
        self,
        session: SessionContext,
        publication_id: str,
        approved_at: str,
        rationale: str,
    ) -> PublicationRequest:
        require_action(session, "approve_publication")
        request = self.publications[publication_id]
        if request.status != "requested":
            raise ValueError("Publication is not awaiting approval")
        if request.requested_by == session.subject_id:
            raise PermissionError("Requester cannot approve own publication")
        request.status = "approved"
        request.approved_by = session.subject_id
        request.approved_at = approved_at
        self._audit(
            session, "approve_publication", request.case_id, request.id,
            "success", approved_at, {"rationale": rationale},
        )
        return request

    def publish(
        self,
        session: SessionContext,
        publication_id: str,
        published_at: str,
    ) -> PublicationRequest:
        require_action(session, "publish")
        request = self.publications[publication_id]
        if request.status != "approved" or not request.approved_by:
            raise ValueError("Publication lacks independent approval")
        request.status = "published"
        request.published_at = published_at
        self._audit(
            session, "publish", request.case_id, request.id,
            "success", published_at,
        )
        return request

    def correct_publication(
        self,
        session: SessionContext,
        publication_id: str,
        corrected_at: str,
        reason: str,
    ) -> PublicationRequest:
        require_action(session, "correct_publication")
        request = self.publications[publication_id]
        if request.status != "published":
            raise ValueError("Only a published item can be corrected")
        request.status = "stale"
        request.stale_reason = reason
        self._audit(
            session, "correct_publication", request.case_id, request.id,
            "success", corrected_at, {"reason": reason},
        )
        return request

    def export_public(
        self,
        session: SessionContext,
        publication_id: str,
        exported_at: str,
    ) -> dict[str, Any]:
        require_action(session, "export_public")
        request = self.publications[publication_id]
        if request.status != "published":
            raise ValueError("Only current published requests may be exported")
        claims = []
        for claim_id in request.claim_ids:
            record = self.records[claim_id]
            if record.data_zone != "public" or record.review_state != "approved":
                raise ValueError("Public export contains unapproved or sensitive record")
            claims.append({
                "id": record.id,
                "title": record.title,
                "payload": record.payload,
                "source_refs": list(record.source_refs),
            })
        payload = {
            "schema_version": "safetrace.public-export/1.6",
            "publication_id": request.id,
            "case_id": request.case_id,
            "exported_at": exported_at,
            "claims": claims,
            "internal_comments_included": False,
            "internal_tasks_included": False,
            "agent_proposals_included": False,
        }
        self._audit(
            session, "export_public", request.case_id, request.id,
            "success", exported_at, {"export_hash": digest(payload)},
        )
        return payload

    def verify_audit_chain(self) -> dict[str, Any]:
        previous_hash = None
        errors: list[str] = []
        for expected_sequence, event in enumerate(self.audit, start=1):
            body = {
                "sequence": event.sequence,
                "case_id": event.case_id,
                "actor_id": event.actor_id,
                "action": event.action,
                "subject_id": event.subject_id,
                "outcome": event.outcome,
                "occurred_at": event.occurred_at,
                "previous_hash": event.previous_hash,
                "details": event.details,
            }
            if event.sequence != expected_sequence:
                errors.append(f"Unexpected audit sequence at {event.id}")
            if event.previous_hash != previous_hash:
                errors.append(f"Broken previous hash at {event.id}")
            if event.event_hash != digest(body):
                errors.append(f"Invalid event hash at {event.id}")
            previous_hash = event.event_hash
        return {
            "status": "pass" if not errors else "fail",
            "events": len(self.audit),
            "head_hash": previous_hash,
            "errors": errors,
        }
