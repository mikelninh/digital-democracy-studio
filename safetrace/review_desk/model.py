from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

EVIDENCE_ROLES = {"supporting", "contradicting", "context"}
EVIDENCE_STATES = {
    "verified_fact",
    "court_established",
    "official_allegation",
    "analytical_red_flag",
    "unresolved_gap",
    "corrected_or_disproved",
}
DECISIONS = {"approved", "rejected", "needs_changes"}
LEGAL_STATES = {"not_required", "pending", "approved", "rejected"}
REPLY_STATES = {"not_required", "pending", "completed", "declined", "not_contacted"}


@dataclass(frozen=True)
class EvidenceRef:
    id: str
    role: str
    source_id: str
    source_url: str
    source_title: str
    summary: str
    source_anchor: str | None = None

    def validate(self) -> None:
        if self.role not in EVIDENCE_ROLES:
            raise ValueError(f"Unsupported evidence role: {self.role}")
        if not self.source_url.startswith("https://"):
            raise ValueError("Evidence requires an HTTPS source URL")
        if not self.summary:
            raise ValueError("Evidence summary is required")


@dataclass(frozen=True)
class Decision:
    outcome: str
    reviewer_role: str
    rationale: str
    decided_at: str
    legal_review: str = "not_required"
    right_of_reply: str = "not_required"
    contradictory_evidence_addressed: bool = False

    def validate(self) -> None:
        if self.outcome not in DECISIONS:
            raise ValueError(f"Unsupported decision: {self.outcome}")
        if self.legal_review not in LEGAL_STATES:
            raise ValueError(f"Unsupported legal review state: {self.legal_review}")
        if self.right_of_reply not in REPLY_STATES:
            raise ValueError(f"Unsupported right-of-reply state: {self.right_of_reply}")
        if not self.reviewer_role or not self.rationale or not self.decided_at:
            raise ValueError("Reviewer role, rationale and timestamp are required")


@dataclass
class Claim:
    id: str
    text: str
    evidence_state: str
    sensitivity: str
    origin: str
    evidence: list[EvidenceRef] = field(default_factory=list)
    decision: Decision | None = None
    correction_history: list[dict[str, Any]] = field(default_factory=list)

    def validate(self) -> None:
        if self.evidence_state not in EVIDENCE_STATES:
            raise ValueError(f"Unsupported evidence state: {self.evidence_state}")
        if self.sensitivity not in {"ordinary", "sensitive"}:
            raise ValueError(f"Unsupported sensitivity: {self.sensitivity}")
        if self.origin not in {"human", "ai_suggested", "imported_official_record"}:
            raise ValueError(f"Unsupported origin: {self.origin}")
        for item in self.evidence:
            item.validate()
        if self.decision:
            self.decision.validate()

    def publication_check(self) -> tuple[bool, list[str]]:
        self.validate()
        blockers: list[str] = []
        support = [item for item in self.evidence if item.role == "supporting"]
        contradictions = [item for item in self.evidence if item.role == "contradicting"]
        if not support:
            blockers.append("missing_supporting_evidence")
        if self.decision is None:
            blockers.append("missing_human_decision")
            return False, blockers
        if self.decision.outcome != "approved":
            blockers.append(f"decision_{self.decision.outcome}")
        if contradictions and not self.decision.contradictory_evidence_addressed:
            blockers.append("contradictory_evidence_not_addressed")
        if self.sensitivity == "sensitive":
            if self.decision.legal_review != "approved":
                blockers.append("sensitive_claim_requires_legal_review")
            if self.decision.right_of_reply not in {"completed", "declined"}:
                blockers.append("sensitive_claim_requires_right_of_reply")
        return not blockers, blockers

    def to_dict(self) -> dict[str, Any]:
        publishable, blockers = self.publication_check()
        payload = asdict(self)
        payload["publication"] = {"publishable": publishable, "blockers": blockers}
        return payload
