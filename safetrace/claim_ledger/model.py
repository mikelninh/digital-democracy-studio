from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from safetrace.core.vocabularies import EVIDENCE_STATES, FIELD_SENSITIVITIES, LEGAL_STATUSES
from .vocabularies import *


def _required(value: str, name: str, minimum: int = 1) -> None:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise ValueError(f"{name} is required")


def _enum(value: str, allowed, name: str) -> None:
    if value not in allowed:
        raise ValueError(f"Unsupported {name}: {value}")


def _time(value: str, name: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc


def as_plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {field.name: as_plain(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(key): as_plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [as_plain(item) for item in value]
    return value


@dataclass(frozen=True)
class VaultEvidenceRef:
    receipt_id: str
    source_id: str
    object_hash: str

    def validate(self) -> None:
        _required(self.receipt_id, "Receipt id")
        _required(self.source_id, "Source id")
        _required(self.object_hash, "Object hash")


@dataclass(frozen=True)
class EvidenceLink:
    id: str
    claim_id: str
    version: int
    role: str
    provenance_mode: str
    source_id: str
    anchor: str
    summary: str
    added_by: str
    added_at: str
    receipt_id: str | None = None
    object_hash: str | None = None
    legacy_url: str | None = None

    def validate(self, vault_index: dict[str, VaultEvidenceRef]) -> None:
        for value, name in (
            (self.id, "Evidence link id"), (self.claim_id, "Claim id"),
            (self.source_id, "Source id"), (self.anchor, "Evidence anchor"),
            (self.summary, "Evidence summary"), (self.added_by, "Evidence contributor"),
        ):
            _required(value, name)
        if self.version < 1:
            raise ValueError("Evidence version must be positive")
        _enum(self.role, EVIDENCE_ROLES, "evidence role")
        _enum(self.provenance_mode, PROVENANCE_MODES, "provenance mode")
        _time(self.added_at, "Evidence added_at")
        if self.provenance_mode == "vault_receipt":
            if not self.receipt_id or not self.object_hash:
                raise ValueError("Vault evidence requires receipt and object hash")
            reference = vault_index.get(self.receipt_id)
            if not reference:
                raise ValueError(f"Unknown vault receipt: {self.receipt_id}")
            if reference.source_id != self.source_id or reference.object_hash != self.object_hash:
                raise ValueError("Vault evidence does not match receipt")
        elif not self.legacy_url:
            raise ValueError("Legacy evidence requires original URL")


@dataclass(frozen=True)
class ClaimVersion:
    claim_id: str
    version: int
    text: str
    evidence_state: str
    legal_status: str
    sensitivity: str
    created_by: str
    created_at: str
    evidence_links: tuple[EvidenceLink, ...]
    limitations: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    supersedes_version: int | None = None

    def validate(
        self,
        vault_index: dict[str, VaultEvidenceRef],
        *,
        require_supporting: bool = True,
    ) -> None:
        _required(self.claim_id, "Claim id")
        _required(self.text, "Claim text", 10)
        _required(self.created_by, "Researcher")
        _time(self.created_at, "Claim version created_at")
        _enum(self.evidence_state, EVIDENCE_STATES, "evidence state")
        _enum(self.legal_status, LEGAL_STATUSES, "legal status")
        _enum(self.sensitivity, FIELD_SENSITIVITIES, "sensitivity")
        if self.version < 1:
            raise ValueError("Claim version must be positive")
        if self.version == 1 and self.supersedes_version is not None:
            raise ValueError("First version cannot supersede another version")
        if self.version > 1 and self.supersedes_version != self.version - 1:
            raise ValueError("Claim versions must form a sequential chain")
        ids: set[str] = set()
        for link in self.evidence_links:
            link.validate(vault_index)
            if link.claim_id != self.claim_id or link.version != self.version:
                raise ValueError("Evidence link is attached to wrong claim version")
            if link.id in ids:
                raise ValueError("Duplicate evidence link")
            ids.add(link.id)
        if require_supporting and not any(link.role == "supporting" for link in self.evidence_links):
            raise ValueError("Claim version requires supporting evidence")

    @property
    def vault_backed(self) -> bool:
        return all(link.provenance_mode == "vault_receipt" for link in self.evidence_links)


@dataclass
class LedgerClaim:
    id: str
    case_id: str
    researcher_id: str
    material: bool
    status: str
    current_version: int
    created_at: str
    updated_at: str
    versions: dict[int, ClaimVersion] = field(default_factory=dict)

    def validate(self, vault_index: dict[str, VaultEvidenceRef]) -> None:
        _required(self.id, "Ledger claim id")
        _required(self.case_id, "Case id")
        _required(self.researcher_id, "Researcher id")
        _enum(self.status, CLAIM_STATUSES, "claim status")
        _time(self.created_at, "Claim created_at")
        _time(self.updated_at, "Claim updated_at")
        if self.current_version not in self.versions:
            raise ValueError("Current claim version is missing")
        for number, version in sorted(self.versions.items()):
            if number != version.version or version.claim_id != self.id:
                raise ValueError("Claim version map is inconsistent")
            # SafeTrace must preserve rejected, disproved and unresolved internal records.
            # They may lack supporting evidence by design, but evaluation still blocks
            # publication because ClaimVersion.validate defaults to require_supporting=True.
            version.validate(vault_index, require_supporting=self.material)


@dataclass(frozen=True)
class ReviewTask:
    id: str
    claim_id: str
    version: int
    gate: str
    assignee_id: str
    status: str
    created_at: str
    required: bool = True

    def validate(self) -> None:
        _required(self.id, "Review task id")
        _required(self.claim_id, "Claim id")
        _required(self.assignee_id, "Assignee")
        _enum(self.gate, REVIEW_GATES, "review gate")
        _enum(self.status, TASK_STATUSES, "task status")
        _time(self.created_at, "Task created_at")


@dataclass(frozen=True)
class ReviewDecision:
    id: str
    task_id: str
    reviewer_id: str
    outcome: str
    rationale: str
    decided_at: str
    contradictory_evidence_addressed: bool = False

    def validate(self) -> None:
        _required(self.id, "Decision id")
        _required(self.task_id, "Task id")
        _required(self.reviewer_id, "Reviewer")
        _enum(self.outcome, TASK_STATUSES - {"pending"}, "decision outcome")
        _required(self.rationale, "Decision rationale", 10)
        _time(self.decided_at, "Decision decided_at")


@dataclass
class LedgerPublication:
    id: str
    case_id: str
    claim_versions: tuple[tuple[str, int], ...]
    status: str
    created_at: str
    published_at: str | None = None
    stale_reason: str | None = None

    def validate(self) -> None:
        _required(self.id, "Publication id")
        _required(self.case_id, "Case id")
        _enum(self.status, PUBLICATION_STATUSES, "publication status")
        _time(self.created_at, "Publication created_at")
        if not self.claim_versions:
            raise ValueError("Publication requires at least one claim version")
        if self.published_at:
            _time(self.published_at, "Publication published_at")


@dataclass(frozen=True)
class LedgerCorrection:
    id: str
    claim_id: str
    from_version: int
    to_version: int
    correction_type: str
    reason: str
    approved_by: str
    corrected_at: str
    visible: bool
    invalidated_publication_ids: tuple[str, ...]

    def validate(self) -> None:
        _required(self.id, "Correction id")
        _required(self.claim_id, "Claim id")
        _enum(self.correction_type, CORRECTION_TYPES, "correction type")
        _required(self.reason, "Correction reason", 10)
        _required(self.approved_by, "Correction approver")
        _time(self.corrected_at, "Correction timestamp")
        if self.to_version != self.from_version + 1:
            raise ValueError("Correction versions must be sequential")
        if not self.visible:
            raise ValueError("Corrections must remain visible")


@dataclass(frozen=True)
class GateResult:
    ready: bool
    blockers: tuple[str, ...]
    required_gates: tuple[str, ...]
