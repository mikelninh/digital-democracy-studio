from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .vocabularies import (
    CASE_STATUSES, DATA_ZONES, PUBLICATION_STATES, RECORD_KINDS,
    REVIEW_STATES, ROLES, SCHEMA_VERSION, TASK_STATUSES,
)


def required(value: str, name: str, minimum: int = 1) -> None:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ValueError(f"{name} is required")


def iso(value: str, name: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: plain(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [plain(item) for item in value]
    return value


@dataclass(frozen=True)
class SessionContext:
    subject_id: str
    role: str
    authenticated: bool
    identity_provider: str
    session_id: str
    data_zone_ceiling: str
    issued_at: str

    def validate(self) -> None:
        for value, name in (
            (self.subject_id, "Subject id"), (self.identity_provider, "Identity provider"),
            (self.session_id, "Session id"),
        ):
            required(value, name)
        if not self.authenticated:
            raise PermissionError("Authenticated internal session required")
        if self.role not in ROLES:
            raise PermissionError("Unknown Desk role")
        if self.data_zone_ceiling not in DATA_ZONES:
            raise PermissionError("Unsupported session data-zone ceiling")
        iso(self.issued_at, "Session issued_at")


@dataclass
class DeskCase:
    id: str
    title: str
    question: str
    status: str
    case_lead: str
    data_zone: str
    public_interest_rationale: str
    publication_boundary: str
    created_at: str
    updated_at: str

    def validate(self) -> None:
        for value, name, minimum in (
            (self.id, "Case id", 1), (self.title, "Case title", 3),
            (self.question, "Case question", 10), (self.case_lead, "Case lead", 1),
            (self.public_interest_rationale, "Public-interest rationale", 15),
            (self.publication_boundary, "Publication boundary", 15),
        ):
            required(value, name, minimum)
        if self.status not in CASE_STATUSES:
            raise ValueError("Unsupported case status")
        if self.data_zone not in DATA_ZONES:
            raise ValueError("Unsupported case data zone")
        iso(self.created_at, "Case created_at")
        iso(self.updated_at, "Case updated_at")


@dataclass
class DeskRecord:
    id: str
    case_id: str
    kind: str
    title: str
    status: str
    data_zone: str
    created_by: str
    created_at: str
    payload: dict[str, Any] = field(default_factory=dict)
    source_refs: tuple[str, ...] = ()
    review_state: str = "draft"

    def validate(self) -> None:
        for value, name in (
            (self.id, "Record id"), (self.case_id, "Record case_id"),
            (self.title, "Record title"), (self.created_by, "Record creator"),
        ):
            required(value, name)
        if self.kind not in RECORD_KINDS:
            raise ValueError("Unsupported record kind")
        if self.data_zone not in DATA_ZONES:
            raise ValueError("Unsupported record data zone")
        if self.review_state not in REVIEW_STATES:
            raise ValueError("Unsupported record review state")
        iso(self.created_at, "Record created_at")


@dataclass
class TeamTask:
    id: str
    case_id: str
    title: str
    assignee_id: str
    status: str
    created_by: str
    created_at: str
    due_at: str | None = None
    blocker: str | None = None

    def validate(self) -> None:
        for value, name in (
            (self.id, "Task id"), (self.case_id, "Task case_id"),
            (self.title, "Task title"), (self.assignee_id, "Task assignee"),
            (self.created_by, "Task creator"),
        ):
            required(value, name)
        if self.status not in TASK_STATUSES:
            raise ValueError("Unsupported task status")
        iso(self.created_at, "Task created_at")
        if self.due_at:
            iso(self.due_at, "Task due_at")


@dataclass(frozen=True)
class DeskComment:
    id: str
    case_id: str
    subject_id: str
    author_id: str
    body: str
    created_at: str

    def validate(self) -> None:
        for value, name, minimum in (
            (self.id, "Comment id", 1), (self.case_id, "Comment case_id", 1),
            (self.subject_id, "Comment subject", 1), (self.author_id, "Comment author", 1),
            (self.body, "Comment body", 3),
        ):
            required(value, name, minimum)
        iso(self.created_at, "Comment created_at")


@dataclass(frozen=True)
class DeskDecision:
    id: str
    case_id: str
    subject_id: str
    decision_type: str
    outcome: str
    reviewer_id: str
    rationale: str
    decided_at: str

    def validate(self) -> None:
        for value, name, minimum in (
            (self.id, "Decision id", 1), (self.case_id, "Decision case_id", 1),
            (self.subject_id, "Decision subject", 1),
            (self.decision_type, "Decision type", 1), (self.outcome, "Decision outcome", 1),
            (self.reviewer_id, "Decision reviewer", 1), (self.rationale, "Decision rationale", 10),
        ):
            required(value, name, minimum)
        iso(self.decided_at, "Decision decided_at")


@dataclass
class PublicationRequest:
    id: str
    case_id: str
    claim_ids: tuple[str, ...]
    status: str
    requested_by: str
    requested_at: str
    approved_by: str | None = None
    approved_at: str | None = None
    published_at: str | None = None
    stale_reason: str | None = None

    def validate(self) -> None:
        required(self.id, "Publication request id")
        required(self.case_id, "Publication case_id")
        required(self.requested_by, "Publication requester")
        if not self.claim_ids:
            raise ValueError("Publication requires claim ids")
        if self.status not in PUBLICATION_STATES:
            raise ValueError("Unsupported publication status")
        iso(self.requested_at, "Publication requested_at")
        if self.approved_at:
            iso(self.approved_at, "Publication approved_at")
        if self.published_at:
            iso(self.published_at, "Publication published_at")


@dataclass(frozen=True)
class AuditEvent:
    id: str
    sequence: int
    case_id: str
    actor_id: str
    action: str
    subject_id: str
    outcome: str
    occurred_at: str
    previous_hash: str | None
    event_hash: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ViewSnapshot:
    view: str
    generated_for: str
    generated_at: str
    items: tuple[dict[str, Any], ...]
    blockers: tuple[str, ...] = ()
    authoritative_system: str = SCHEMA_VERSION
