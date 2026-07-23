from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any

PROPOSAL_KINDS = {"no_change", "material_source_change", "deadline_passed_unresolved"}
REVIEW_STATES = {"not_required", "pending_review", "approved", "rejected"}


@dataclass(frozen=True)
class SnapshotState:
    source_id: str
    canonical_url: str
    checked_at: str
    raw_sha256: str
    normalized_sha256: str
    parser_version: str

    def validate(self) -> None:
        if not self.source_id or not self.canonical_url.startswith("https://"):
            raise ValueError("Source id and HTTPS URL are required")
        for digest in (self.raw_sha256, self.normalized_sha256):
            if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest.lower()):
                raise ValueError("Snapshot hashes must be SHA-256 hex digests")


@dataclass
class ChangeProposal:
    id: str
    kind: str
    source_id: str
    created_at: str
    summary: str
    evidence: list[dict[str, Any]]
    review_state: str
    public_effect: str = "none_until_human_approval"
    reviewer_role: str | None = None
    review_rationale: str | None = None
    reviewed_at: str | None = None
    affected_claims: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.kind not in PROPOSAL_KINDS:
            raise ValueError(f"Unsupported proposal kind: {self.kind}")
        if self.review_state not in REVIEW_STATES:
            raise ValueError(f"Unsupported review state: {self.review_state}")
        if self.kind == "no_change" and self.review_state != "not_required":
            raise ValueError("No-change proposals do not require editorial review")
        if self.review_state in {"approved", "rejected"}:
            if not self.reviewer_role or not self.review_rationale or not self.reviewed_at:
                raise ValueError("Completed reviews require reviewer, rationale and timestamp")

    def can_change_public_status(self) -> bool:
        self.validate()
        return self.review_state == "approved"

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        payload = asdict(self)
        payload["can_change_public_status"] = self.can_change_public_status()
        return payload


def compare_snapshots(previous: SnapshotState, current: SnapshotState, *, created_at: str) -> ChangeProposal:
    previous.validate()
    current.validate()
    if previous.source_id != current.source_id:
        raise ValueError("Snapshots must describe the same source")
    if previous.normalized_sha256 == current.normalized_sha256:
        return ChangeProposal(
            id=f"proposal:{current.source_id}:{created_at}",
            kind="no_change",
            source_id=current.source_id,
            created_at=created_at,
            summary="No material source change detected after normalisation.",
            evidence=[{"previous": previous.raw_sha256, "current": current.raw_sha256}],
            review_state="not_required",
        )
    return ChangeProposal(
        id=f"proposal:{current.source_id}:{created_at}",
        kind="material_source_change",
        source_id=current.source_id,
        created_at=created_at,
        summary="The normalised official source changed. A human must inspect the diff before any public claim changes.",
        evidence=[
            {
                "previous_raw_sha256": previous.raw_sha256,
                "current_raw_sha256": current.raw_sha256,
                "previous_normalized_sha256": previous.normalized_sha256,
                "current_normalized_sha256": current.normalized_sha256,
                "previous_checked_at": previous.checked_at,
                "current_checked_at": current.checked_at,
            }
        ],
        review_state="pending_review",
    )


def deadline_proposal(
    *,
    item_id: str,
    source_id: str,
    deadline: date,
    checked_on: date,
    unresolved: bool,
    source_url: str,
    careful_interpretation: str,
) -> ChangeProposal | None:
    if not unresolved or checked_on <= deadline:
        return None
    return ChangeProposal(
        id=f"proposal:deadline:{item_id}:{checked_on.isoformat()}",
        kind="deadline_passed_unresolved",
        source_id=source_id,
        created_at=checked_on.isoformat(),
        summary=f"A publicly stated deadline of {deadline.isoformat()} has passed and the monitored question remains unresolved in the public record.",
        evidence=[
            {
                "deadline": deadline.isoformat(),
                "checked_on": checked_on.isoformat(),
                "source_url": source_url,
                "careful_interpretation": careful_interpretation,
            }
        ],
        review_state="pending_review",
        affected_claims=[item_id],
    )
