from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Literal

Sensitivity = Literal["public", "personal", "sensitive"]
Retention = Literal["ephemeral", "case_session", "explicit_retention"]


@dataclass(frozen=True)
class EvidenceVaultReceipt:
    evidence_id: str
    sha256: str
    bytes_seen: int
    media_type: str
    sensitivity: Sensitivity
    retention: Retention
    created_at: str
    expires_at: str | None
    raw_persisted: bool
    redaction_required_before_export: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def ingest_bytes(
    payload: bytes,
    *,
    media_type: str,
    sensitivity: Sensitivity = "personal",
    retention: Retention = "ephemeral",
    evidence_id: str = "evidence-local",
    case_session_hours: int = 24,
) -> EvidenceVaultReceipt:
    """Create an integrity receipt without persisting raw user evidence.

    The master proof deliberately defaults to `ephemeral`: bytes are hashed in
    memory and discarded by this function. Production storage needs an explicit
    encrypted store, access policy, deletion job and audit trail; this module
    must not be mistaken for those controls.
    """
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if retention not in {"ephemeral", "case_session", "explicit_retention"}:
        raise ValueError("unsupported retention policy")
    now = datetime.now(timezone.utc)
    expires_at: str | None = None
    if retention == "case_session":
        expires_at = (now + timedelta(hours=case_session_hours)).isoformat()
    # Raw persistence is intentionally unsupported in this proof. A caller must
    # integrate a reviewed encrypted Evidence Vault for explicit retention.
    raw_persisted = False
    return EvidenceVaultReceipt(
        evidence_id=evidence_id,
        sha256=hashlib.sha256(payload).hexdigest(),
        bytes_seen=len(payload),
        media_type=media_type,
        sensitivity=sensitivity,
        retention=retention,
        created_at=now.isoformat(),
        expires_at=expires_at,
        raw_persisted=raw_persisted,
        redaction_required_before_export=sensitivity in {"personal", "sensitive"},
    )


def export_policy(receipt: EvidenceVaultReceipt) -> dict[str, Any]:
    """Return the gate that must be cleared before evidence leaves the case."""
    return {
        "allowed": receipt.sensitivity == "public",
        "requires_human_approval": receipt.sensitivity != "public",
        "requires_redaction_review": receipt.redaction_required_before_export,
        "reason": (
            "Public evidence may be referenced after provenance verification."
            if receipt.sensitivity == "public"
            else "Personal/sensitive evidence requires redaction review and explicit human approval before export."
        ),
    }
