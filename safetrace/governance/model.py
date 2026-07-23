from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

CONTROL_STATUSES = {"implemented", "documented", "blocked", "not_applicable"}
CONTROL_DOMAINS = {"access", "privacy", "security", "governance", "legal", "operations"}
DATA_CLASSES = {"public", "synthetic", "restricted_partner", "victim_sensitive"}
PILOT_MODES = {"synthetic_evaluation", "restricted_partner"}

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "public_reader": frozenset({"read_public"}),
    "researcher": frozenset({"read_public", "create_draft", "attach_evidence"}),
    "reviewer": frozenset({"read_public", "create_draft", "attach_evidence", "review_claim"}),
    "legal_reviewer": frozenset({"read_public", "review_claim", "approve_sensitive"}),
    "partner_operator": frozenset({"read_public", "read_restricted", "create_draft", "attach_evidence"}),
    "security_admin": frozenset({"read_public", "read_restricted", "inspect_audit_log", "manage_access"}),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class Control:
    id: str
    domain: str
    description: str
    status: str
    required_for: list[str]
    owner_role: str
    evidence: list[str] = field(default_factory=list)
    last_reviewed: str | None = None
    blocker: str | None = None

    def validate(self) -> None:
        if self.domain not in CONTROL_DOMAINS:
            raise ValueError(f"Unsupported control domain: {self.domain}")
        if self.status not in CONTROL_STATUSES:
            raise ValueError(f"Unsupported control status: {self.status}")
        if not self.id or not self.description or not self.owner_role:
            raise ValueError("Control id, description and owner role are required")
        if self.status in {"implemented", "documented"} and not self.evidence:
            raise ValueError(f"Control {self.id} needs evidence")
        if self.status == "blocked" and not self.blocker:
            raise ValueError(f"Blocked control {self.id} needs a blocker explanation")


@dataclass(frozen=True)
class PilotBoundary:
    mode: str
    allowed_data_classes: list[str]
    personal_data_allowed: bool
    victim_or_witness_data_allowed: bool
    automated_publication_allowed: bool
    automated_referral_allowed: bool
    named_partner_required: bool

    def validate(self) -> None:
        if self.mode not in PILOT_MODES:
            raise ValueError(f"Unsupported pilot mode: {self.mode}")
        invalid = set(self.allowed_data_classes) - DATA_CLASSES
        if invalid:
            raise ValueError(f"Unsupported data classes: {sorted(invalid)}")
        if self.automated_publication_allowed or self.automated_referral_allowed:
            raise ValueError("SafeTrace never permits autonomous publication or referral")
        if self.mode == "synthetic_evaluation":
            if self.personal_data_allowed or self.victim_or_witness_data_allowed:
                raise ValueError("Synthetic evaluation cannot allow personal or victim data")
            if set(self.allowed_data_classes) - {"public", "synthetic"}:
                raise ValueError("Synthetic evaluation is limited to public and synthetic data")


@dataclass(frozen=True)
class ReadinessAssessment:
    mode: str
    ready: bool
    blockers: list[str]
    satisfied_controls: int
    required_controls: int
    boundary: PilotBoundary

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["readiness_ratio"] = (
            self.satisfied_controls / self.required_controls if self.required_controls else 1.0
        )
        return payload


def evaluate_readiness(
    controls: Iterable[Control],
    boundary: PilotBoundary,
) -> ReadinessAssessment:
    boundary.validate()
    controls = list(controls)
    for control in controls:
        control.validate()

    required = [item for item in controls if boundary.mode in item.required_for]
    blockers: list[str] = []
    satisfied = 0
    for item in required:
        if item.status in {"implemented", "documented"}:
            satisfied += 1
        else:
            blockers.append(f"{item.id}: {item.blocker or item.status}")

    if boundary.mode == "restricted_partner" and boundary.named_partner_required:
        blockers.append("partner: a qualified partner and signed operating agreement are required")

    return ReadinessAssessment(
        mode=boundary.mode,
        ready=not blockers,
        blockers=blockers,
        satisfied_controls=satisfied,
        required_controls=len(required),
        boundary=boundary,
    )


def is_authorized(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, frozenset())


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    occurred_at: str
    actor_role: str
    action: str
    resource_id: str
    outcome: str
    metadata: dict[str, Any]
    previous_hash: str
    event_hash: str

    def unsigned_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("event_hash")
        return payload


class AuditLog:
    """Append-only, hash-chained audit log for the pilot prototype."""

    def __init__(self, events: Iterable[AuditEvent] | None = None):
        self.events = list(events or [])

    @property
    def latest_hash(self) -> str:
        return self.events[-1].event_hash if self.events else "0" * 64

    def append(
        self,
        *,
        event_id: str,
        actor_role: str,
        action: str,
        resource_id: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
        occurred_at: str | None = None,
    ) -> AuditEvent:
        if not is_authorized(actor_role, action):
            outcome = "denied"
        unsigned = {
            "event_id": event_id,
            "occurred_at": occurred_at or utc_now(),
            "actor_role": actor_role,
            "action": action,
            "resource_id": resource_id,
            "outcome": outcome,
            "metadata": metadata or {},
            "previous_hash": self.latest_hash,
        }
        event_hash = hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()
        event = AuditEvent(**unsigned, event_hash=event_hash)
        self.events.append(event)
        return event

    def verify(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        expected_previous = "0" * 64
        for index, event in enumerate(self.events):
            if event.previous_hash != expected_previous:
                errors.append(f"event[{index}] previous hash mismatch")
            expected_hash = hashlib.sha256(
                canonical_json(event.unsigned_payload()).encode("utf-8")
            ).hexdigest()
            if event.event_hash != expected_hash:
                errors.append(f"event[{index}] event hash mismatch")
            expected_previous = event.event_hash
        return not errors, errors

    def to_dict(self) -> dict[str, Any]:
        valid, errors = self.verify()
        return {
            "schema_version": "safetrace.audit-log/1.0",
            "valid": valid,
            "errors": errors,
            "events": [asdict(item) for item in self.events],
        }


def load_governance(path: str | Path) -> tuple[list[Control], dict[str, PilotBoundary]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    controls = [Control(**item) for item in payload["controls"]]
    boundaries = {
        name: PilotBoundary(**definition)
        for name, definition in payload["boundaries"].items()
    }
    return controls, boundaries
