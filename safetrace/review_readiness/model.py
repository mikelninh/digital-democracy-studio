from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

DISCIPLINES = frozenset({
    "investigative_editorial", "privacy", "legal", "security", "domain",
    "accessibility", "public_comprehension",
})
SEVERITIES = frozenset({"critical", "high", "medium", "low", "info"})
FINDING_STATUSES = frozenset({"open", "in_remediation", "resolved", "accepted_risk"})
DISCLOSURE_DECISIONS = frozenset({"public", "public_after_remediation", "restricted_security_detail", "pending"})


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
class ReviewSlot:
    discipline: str
    purpose: str
    minimum_qualification: str
    independent_required: bool
    external_reviewer_id: str | None = None
    conflict_declaration_id: str | None = None
    status: str = "unassigned"

    def validate(self) -> None:
        if self.discipline not in DISCIPLINES:
            raise ValueError("Unsupported review discipline")
        required(self.purpose, "Review purpose", 15)
        required(self.minimum_qualification, "Minimum qualification", 10)
        if self.status not in {"unassigned", "invited", "in_review", "completed"}:
            raise ValueError("Unsupported review-slot status")
        if self.status == "completed" and not self.external_reviewer_id:
            raise ValueError("Completed external review requires a reviewer identity")


@dataclass(frozen=True)
class ReviewPacket:
    id: str
    discipline: str
    scope: str
    artifact_hashes: dict[str, str]
    questions: tuple[str, ...]
    expected_outputs: tuple[str, ...]
    created_at: str

    def validate(self) -> None:
        required(self.id, "Packet id")
        if self.discipline not in DISCIPLINES:
            raise ValueError("Unsupported packet discipline")
        required(self.scope, "Review scope", 20)
        if not self.artifact_hashes or not all(len(value) == 64 for value in self.artifact_hashes.values()):
            raise ValueError("Review packet requires SHA-256 artifact hashes")
        if not self.questions or not self.expected_outputs:
            raise ValueError("Review packet requires questions and outputs")
        iso(self.created_at, "Packet created_at")


@dataclass
class Finding:
    id: str
    discipline: str
    title: str
    severity: str
    status: str
    owner: str
    remediation: str
    disclosure_decision: str
    opened_at: str
    synthetic_dry_run: bool
    resolved_at: str | None = None
    evidence_refs: tuple[str, ...] = ()

    def validate(self) -> None:
        required(self.id, "Finding id")
        if self.discipline not in DISCIPLINES:
            raise ValueError("Unsupported finding discipline")
        required(self.title, "Finding title", 8)
        if self.severity not in SEVERITIES:
            raise ValueError("Unsupported finding severity")
        if self.status not in FINDING_STATUSES:
            raise ValueError("Unsupported finding status")
        required(self.owner, "Finding owner")
        required(self.remediation, "Finding remediation", 15)
        if self.disclosure_decision not in DISCLOSURE_DECISIONS:
            raise ValueError("Unsupported disclosure decision")
        iso(self.opened_at, "Finding opened_at")
        if self.status == "resolved" and not self.resolved_at:
            raise ValueError("Resolved finding requires resolved_at")


@dataclass(frozen=True)
class Exercise:
    id: str
    exercise_type: str
    scenario: str
    objectives: tuple[str, ...]
    steps: tuple[str, ...]
    observed_gaps: tuple[str, ...]
    conducted_at: str
    mode: str
    external_observer_present: bool

    def validate(self) -> None:
        required(self.id, "Exercise id")
        if self.exercise_type not in {"threat_model_workshop", "incident_tabletop", "recovery_drill"}:
            raise ValueError("Unsupported exercise type")
        required(self.scenario, "Exercise scenario", 15)
        if not self.objectives or not self.steps:
            raise ValueError("Exercise requires objectives and steps")
        if self.mode not in {"synthetic_dry_run", "observed_external"}:
            raise ValueError("Unsupported exercise mode")
        if self.mode == "observed_external" and not self.external_observer_present:
            raise ValueError("Observed external exercise requires an external observer")
        iso(self.conducted_at, "Exercise conducted_at")


@dataclass(frozen=True)
class StudyProtocol:
    id: str
    study_type: str
    objective: str
    participant_requirements: tuple[str, ...]
    consent_required: bool
    collected_fields: tuple[str, ...]
    prohibited_fields: tuple[str, ...]
    metrics: tuple[str, ...]
    stopping_rules: tuple[str, ...]
    status: str

    def validate(self) -> None:
        required(self.id, "Protocol id")
        if self.study_type not in {"workflow_benchmark", "citizen_comprehension"}:
            raise ValueError("Unsupported study type")
        required(self.objective, "Study objective", 15)
        if not self.participant_requirements or not self.metrics or not self.stopping_rules:
            raise ValueError("Study protocol is incomplete")
        if not self.consent_required:
            raise ValueError("External study protocol must require consent")
        if self.status not in {"draft", "ready_for_ethics_privacy_review", "approved", "completed"}:
            raise ValueError("Unsupported protocol status")
        if self.status in {"approved", "completed"}:
            raise ValueError("v1.8 cannot self-approve an external study protocol")


@dataclass(frozen=True)
class ReadinessDecision:
    status: str
    external_reviews_completed: int
    external_approvals: int
    unresolved_critical_findings: int
    unresolved_high_findings: int
    ready_to_invite_reviewers: bool
    restricted_data_gate_open: bool
    partner_pilot_gate_open: bool
    reasons: tuple[str, ...]
